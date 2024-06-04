import json
from datetime import timedelta

import pdfkit
import stripe
from dateutil import parser
from rest_framework import mixins, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils import timezone

from apps.account.models import Account
from apps.billing.api.v1.serializers import InvoiceSerializer, TransactionSerializer
from apps.billing.models import Invoice, Transaction
from la.settings import (
    DEFAULT_DOMAIN,
    STRIPE_SECRET_KEY,
    SUBSCRIPTION_PERIOD_DAYS,
    TRIAL_PERIOD_DAYS,
    hashids,
)


class InvoiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """Вью для отображения инвойсов."""

    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.select_related().filter(account=self.request.user)


def checkout_session(account, invoice):
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': int(invoice.service.cost) * 100,
                    'product_data': {
                        'name': invoice.service.name,
                    },
                },
                'quantity': 1,
            },
        ],
        metadata={'invoice_id': invoice.id, 'account_id': invoice.account.id},
        mode='payment',
        success_url=DEFAULT_DOMAIN + '/payment-thank-you',
        cancel_url=DEFAULT_DOMAIN + '/payment-error',
    )
    Transaction.objects.create(
        account=invoice.account,
        invoice=invoice,
        stripe_session_id=checkout_session.id,
        sum=invoice.service.cost,
    )
    return checkout_session.url


class CheckoutSessionView(APIView):
    def get(self, request, *args, **kwargs):
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            invoice = (
                Invoice.objects.select_related()
                .filter(
                    ~Q(paid_status=Invoice.PaidStatus.PAID.value)
                    & ~Q(paid_status=Invoice.PaidStatus.CANCELED.value),
                    account=request.user,
                    id=kwargs['invoice_id'],
                )
                .first()
            )
            if not invoice:
                raise Invoice.DoesNotExist()
        except Invoice.DoesNotExist:
            raise NotFound()
        return Response(
            {'url': checkout_session(invoice.account, invoice)},
            status=status.HTTP_200_OK,
        )


class CheckoutSessionEmailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        invoice_id_decode = hashids.decode(kwargs['hash_invoice_id'])
        if invoice_id_decode:
            invoice_id_decode = invoice_id_decode[0]
        else:
            raise NotFound()
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            invoice = (
                Invoice.objects.select_related()
                .filter(
                    ~Q(paid_status=Invoice.PaidStatus.PAID.value)
                    & ~Q(paid_status=Invoice.PaidStatus.CANCELED.value),
                    id=invoice_id_decode,
                )
                .first()
            )
            if not invoice:
                raise Invoice.DoesNotExist()
        except Invoice.DoesNotExist:
            raise NotFound()
        return HttpResponseRedirect(
            redirect_to=checkout_session(invoice.account, invoice)
        )


class CheckoutWebHookView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):  # noqa: C901
        stripe.api_key = STRIPE_SECRET_KEY
        payload = request.body

        try:
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except ValueError:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if (
            event['type'] == 'checkout.session.completed'
            or event['type'] == 'checkout.session.async_payment_succeeded'
        ):
            transaction = (
                Transaction.objects.select_related()
                .filter(
                    stripe_session_id=event['data']['object']['id'],
                )
                .first()
            )
            if transaction and event['data']['object']['payment_status'] == 'paid':
                transaction.transaction_status = (
                    Transaction.TransactionStatus.SUCCESS.value
                )
                transaction.date_completed = timezone.now()
                transaction.save()

                transaction.invoice.paid_status = Invoice.PaidStatus.PAID.value
                transaction.invoice.date_completed = timezone.now()
                transaction.invoice.save()

                payment_date = timezone.now()
                if (
                    transaction.account.subscription_status
                    == Account.SubscriptionStatus.TRIAL.value
                ):
                    transaction.account.subscription_status = (
                        Account.SubscriptionStatus.SUBSCRIPTION.value
                    )
                    trial_days = transaction.account.date_joined + timedelta(
                        days=TRIAL_PERIOD_DAYS
                    )
                    if timezone.now() < trial_days:
                        payment_date = payment_date + timedelta(
                            minutes=(trial_days - timezone.now()).total_seconds()
                            / 60.0,
                        )

                if all(
                    (
                        transaction.account.last_subscription_payment_date,
                        transaction.account.subscription_status
                        == Account.SubscriptionStatus.SUBSCRIPTION.value,
                    )
                ):
                    subscription_days = (
                        transaction.account.last_subscription_payment_date
                        + timedelta(
                            days=SUBSCRIPTION_PERIOD_DAYS,
                        )
                    )
                    if timezone.now() < subscription_days:
                        payment_date = payment_date + timedelta(
                            minutes=(subscription_days - timezone.now()).total_seconds()
                            / 60.0,
                        )

                transaction.account.last_subscription_payment_date = payment_date
                transaction.account.has_access = True
                transaction.account.save()
                cache.set(f'user_auth{transaction.account.email}', True)
            return Response(status=status.HTTP_200_OK)
        elif event['type'] == 'checkout.session.async_payment_failed':
            session_id = event['data']['object']['id']
            transaction = (
                Transaction.objects.select_related()
                .filter(
                    stripe_session_id=session_id,
                )
                .first()
            )
            if transaction:
                transaction.transaction_status = (
                    Transaction.TransactionStatus.ERROR.value
                )
                transaction.save()
                cache.set(f'user_auth{transaction.account.email}', False)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """Вью для отображения транзакций."""

    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.select_related().filter(account=self.request.user)


class DownloadInvoiceView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            invoice = Invoice.objects.select_related().get(
                date_created=parser.parse(kwargs['date_created']),
                invoice_id=kwargs['invoice_id'],
            )
        except Invoice.DoesNotExist:
            raise NotFound
        country = invoice.account.profile_account.country
        city = invoice.account.profile_account.city

        html = (
            loader.render_to_string(
                '../templates/invoice.html',
                {
                    'invoice_number': str(invoice.invoice_id).split('-')[-1],
                    'account_name': invoice.account.profile_account.real_name,
                    'account_address': invoice.account.profile_account.address,
                    'account_email': invoice.account.email,
                    'invoice_date': invoice.date_created,
                    'invoice_due_date': invoice.due_date,
                    'invoice_cost': invoice.service.cost,
                    'account_country': country.name if country else None,
                    'account_city': city.name if city else None,
                    'subscription_date': timezone.now()
                    + timedelta(days=SUBSCRIPTION_PERIOD_DAYS),
                },
            ),
        )
        options = {
            'page-size': 'Letter',
            'encoding': 'UTF-8',
            'enable-local-file-access': '',
        }
        pdf = pdfkit.from_string(html[0], options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = f'attachment; filename="invoice_{invoice.invoice_id}.pdf"'
        return response
