import uuid

from django.db import models

from apps.account.models import Account
from apps.data.models import Currency  # noqa: F401
from apps.service.models import Service


class Invoice(models.Model):
    class PaidStatus(models.IntegerChoices):
        PAID = 1, 'Paid'
        UNPAID = 2, 'Unpaid'
        CANCELED = 3, 'Canceled'

    account = models.ForeignKey(
        Account, related_name='invoice_account', on_delete=models.PROTECT
    )
    service = models.ForeignKey(
        Service, related_name='invoice_service', on_delete=models.PROTECT
    )
    invoice_id = models.UUIDField(
        'Invoice id',
        default=uuid.uuid4,
        editable=False,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField('Due date', null=True, blank=True)
    paid_status = models.IntegerField(
        'Paid status', choices=PaidStatus.choices, default=PaidStatus.UNPAID
    )
    discount = models.DecimalField(
        'Discount', default=0, max_digits=10, decimal_places=2
    )
    email_notification_date = models.DateTimeField(
        'Email notification date', null=True, blank=True
    )

    def __str__(self):
        return f'{self.account.email}/{self.service.name}'


class Transaction(models.Model):
    class TransactionStatus(models.IntegerChoices):
        SUCCESS = 1, 'Success'
        ERROR = 2, 'Error'
        PROCESS = 3, 'Process'
        CANCELED = 4, 'Canceled'

    account = models.ForeignKey(
        Account, related_name='transaction_account', on_delete=models.PROTECT
    )
    invoice = models.ForeignKey(
        Invoice, related_name='transaction_invoice', on_delete=models.PROTECT
    )
    transaction_id = models.UUIDField(
        'Transaction id',
        default=uuid.uuid4,
        editable=False,
    )
    stripe_session_id = models.CharField(
        'Stripe session id', max_length=255, blank=True
    )
    describe = models.CharField('Describe', max_length=255, default='Invoice Payment')
    sum = models.DecimalField('Sum', max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    transaction_status = models.IntegerField(
        'Paid status',
        choices=TransactionStatus.choices,
        default=TransactionStatus.PROCESS,
    )

    def __str__(self):
        return f'{self.account.email}/{self.invoice.invoice_id}'
