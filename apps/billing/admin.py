import datetime

from rangefilter.filters import DateRangeFilter, NumericRangeFilter

from django.contrib import admin

from apps.billing.models import Invoice, Transaction


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'service',
        'service_cost',
        'invoice_id',
        'date_created',
        'due_date',
        'paid_status',
        'discount',
        'last_subscription_payment_date',
    )
    list_filter = ('paid_status',)
    search_fields = (
        'account__email',
        'service__name',
        'invoice_id',
        'date_created',
        'due_date',
        'paid_status',
        'discount',
    )
    list_select_related = ('account', 'service')
    raw_id_fields = ('account', 'service')

    @admin.display(
        description='service_cost',
        empty_value='0.0',
    )
    def service_cost(self, invoice):
        return invoice.service.cost

    @admin.display(
        description='last_subscription_payment_date',
    )
    def last_subscription_payment_date(self, invoice):
        return invoice.account.last_subscription_payment_date


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'account_email',
        'invoice_id',
        'transaction_id',
        'describe',
        'sum',
        'transaction_status',
        'date_created',
        'date_completed',
    )
    list_filter = (
        ('date_created', DateRangeFilter),
        ('sum', NumericRangeFilter),
    )
    search_fields = (
        'account__email',
        'invoice_id',
        'transaction_id',
        'describe',
        'sum',
        'date_created',
        'transaction_status',
        'date_completed',
    )
    list_select_related = ('account', 'invoice')
    raw_id_fields = ('account', 'invoice')

    def get_rangefilter_date_created_default(self, request):
        return datetime.date.today, datetime.date.today

    @admin.display(
        description='account_email',
        empty_value='-',
    )
    def account_email(self, transaction):
        return transaction.account.email

    @admin.display(
        description='invoice_id',
        empty_value='-',
    )
    def invoice_id(self, transaction):
        return transaction.invoice.invoice_id
