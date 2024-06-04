import os
from datetime import timedelta

from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from apps.account.models import Account
from apps.billing.models import Invoice, Transaction
from apps.billing.utils import send_notification_if_applicable
from apps.notification.models import Notification
from apps.service.models import Service
from la import settings
from la.celery import app
from la.settings import (
    DEFAULT_ACCOUNT_REAL_NAME,
    DEFAULT_DOMAIN,
    SUBSCRIPTION_PERIOD_DAYS,
    SUBSCRIPTION_PERIOD_INVOICE_DAYS_BEFORE,
    TRIAL_PERIOD_DAYS,
    TRIAL_PERIOD_INVOICE_DAYS_BEFORE,
    hashids,
)


@app.task(bind=True)
def create_invoice_payment_background(self):  # noqa: C901
    if settings.INVOICE_ENABLED:
        trial_accounts = Account.objects.select_related().filter(
            subscription_status=Account.SubscriptionStatus.TRIAL.value
        )
        for trial_account in trial_accounts:
            calculate_days = timezone.now() - (
                trial_account.date_joined + timedelta(days=TRIAL_PERIOD_DAYS)
            )
            if all(
                (
                    calculate_days.days >= TRIAL_PERIOD_INVOICE_DAYS_BEFORE,
                    trial_account.invoice_account.filter(
                        paid_status=Invoice.PaidStatus.UNPAID.value
                    ).exists(),
                )
            ):
                invoice = trial_account.invoice_account.filter(
                    paid_status=Invoice.PaidStatus.UNPAID.value
                ).first()
                if not Notification.objects.filter(
                    recipient=trial_account, level='unpaid'
                ).exists():
                    send_notification_if_applicable(
                        recipient=trial_account,
                        message=f'You have a new unpaid invoice for {invoice.service.cost}.',
                        level='unpaid',
                    )
            if all((calculate_days.days >= 0, trial_account.has_access)):
                trial_account.has_access = False
                trial_account.save()
                cache.set(f'user_auth{trial_account.email}', False)

        subscription_accounts = Account.objects.select_related().filter(
            subscription_status=Account.SubscriptionStatus.SUBSCRIPTION.value,
        )

        for subscription_account in subscription_accounts:
            calculate_days = timezone.now() - (
                subscription_account.last_subscription_payment_date
                + timedelta(
                    days=SUBSCRIPTION_PERIOD_DAYS,
                )
            )
            if all(
                (
                    calculate_days.days >= SUBSCRIPTION_PERIOD_INVOICE_DAYS_BEFORE,
                    not subscription_account.invoice_account.filter(
                        paid_status=Invoice.PaidStatus.UNPAID.value
                    ).exists(),
                )
            ):
                create_filter = {
                    'account': subscription_account,
                    'service': Service.objects.get(id=1),
                }
                if subscription_account.last_subscription_payment_date:
                    create_filter.update(
                        {
                            'due_date': subscription_account.last_subscription_payment_date
                            + timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
                        }
                    )
                invoice = Invoice.objects.create(**create_filter)
                if not Notification.objects.filter(
                    recipient=subscription_account, level='unpaid'
                ).exists():
                    send_notification_if_applicable(
                        recipient=subscription_account,
                        message=f'You have a new unpaid invoice for {invoice.service.cost}.',
                        level='unpaid',
                    )
            if all((calculate_days.days >= 0, subscription_account.has_access)):
                subscription_account.has_access = False
                subscription_account.save()
                cache.set(f'user_auth{subscription_account.email}', False)


@app.task(bind=True)
def check_transaction_status_background(self):
    if settings.INVOICE_ENABLED:
        Transaction.objects.filter(
            date_created__lt=timezone.now() - timedelta(hours=1),
            transaction_status=Transaction.TransactionStatus.PROCESS.value,
        ).update(transaction_status=Transaction.TransactionStatus.CANCELED.value)


@app.task(bind=True)
def send_invoice_payment_email_background(self):  # noqa: C901
    if settings.INVOICE_ENABLED:
        trial_accounts = Account.objects.select_related().filter(
            subscription_status=Account.SubscriptionStatus.TRIAL.value
        )
        for trial_account in trial_accounts:
            calculate_days = timezone.now() - (
                trial_account.date_joined + timedelta(days=TRIAL_PERIOD_DAYS)
            )
            if all(
                (
                    calculate_days.days >= TRIAL_PERIOD_INVOICE_DAYS_BEFORE,
                    trial_account.invoice_account.filter(
                        paid_status=Invoice.PaidStatus.UNPAID.value
                    ).exists(),
                )
            ):
                trial_account_invoice = trial_account.invoice_account.filter(
                    paid_status=Invoice.PaidStatus.UNPAID.value,
                ).last()
                if not trial_account.profile_account.real_name:
                    trial_account.profile_account.real_name = DEFAULT_ACCOUNT_REAL_NAME
                if not trial_account_invoice.email_notification_date:
                    html_content = render_to_string(
                        os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),
                            'account/templates/templated_email/subscription_expired.html',
                        ),
                        context={
                            'username': trial_account.profile_account.real_name,
                            'invoice_url': DEFAULT_DOMAIN
                            + reverse(
                                'api-billing:v1:checkout_session_email_view',
                                kwargs={
                                    'hash_invoice_id': hashids.encode(
                                        trial_account_invoice.id
                                    ),
                                    # 'id_hash': hashids.encode(trial_account.id),
                                },
                            ),
                        },
                    ).strip()
                    try:
                        msg = EmailMultiAlternatives(
                            'Subscription is almost expires!',
                            html_content,
                            settings.EMAIL_HOST_USER,
                            [trial_account.email],
                        )
                        msg.content_subtype = 'html'
                        msg.send()
                        trial_account_invoice.email_notification_date = timezone.now()
                        trial_account_invoice.save()
                    except Exception:
                        pass

        subscription_accounts = Account.objects.select_related().filter(
            subscription_status=Account.SubscriptionStatus.SUBSCRIPTION.value,
        )

        for subscription_account in subscription_accounts:
            calculate_days = timezone.now() - (
                subscription_account.last_subscription_payment_date
                + timedelta(
                    days=SUBSCRIPTION_PERIOD_DAYS,
                )
            )
            if all(
                (
                    calculate_days.days >= SUBSCRIPTION_PERIOD_INVOICE_DAYS_BEFORE,
                    subscription_account.invoice_account.filter(
                        paid_status=Invoice.PaidStatus.UNPAID.value
                    ).exists(),
                )
            ):
                subscription_account_invoice = (
                    subscription_account.invoice_account.filter(
                        paid_status=Invoice.PaidStatus.UNPAID.value,
                    ).last()
                )
                if not subscription_account.profile_account.real_name:
                    subscription_account.profile_account.real_name = (
                        DEFAULT_ACCOUNT_REAL_NAME
                    )
                if not subscription_account_invoice.email_notification_date:
                    html_content = render_to_string(
                        os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),
                            'account/templates/templated_email/subscription_expired.html',
                        ),
                        context={
                            'username': subscription_account.profile_account.real_name,
                            'invoice_url': DEFAULT_DOMAIN
                            + reverse(
                                'api-billing:v1:checkout_session_email_view',
                                kwargs={
                                    'hash_invoice_id': hashids.encode(
                                        subscription_account_invoice.id
                                    ),
                                    # 'id_hash': hashids.encode(subscription_account.id),
                                },
                            ),
                        },
                    ).strip()
                    try:
                        msg = EmailMultiAlternatives(
                            'Subscription is almost expires!',
                            html_content,
                            settings.EMAIL_HOST_USER,
                            [subscription_account.email],
                        )
                        msg.content_subtype = 'html'
                        msg.send()
                        subscription_account_invoice.email_notification_date = (
                            timezone.now()
                        )
                        subscription_account_invoice.save()
                    except Exception:
                        pass
