from rest_framework.serializers import ModelSerializer

from apps.account.api.v1.serializers import AccountSerializer
from apps.billing.models import Invoice, Transaction
from apps.service.api.v1.serializers import ServiceSerializer


class InvoiceSerializer(ModelSerializer[Invoice]):
    account = AccountSerializer()
    service = ServiceSerializer()

    class Meta:
        model = Invoice
        fields = '__all__'


class TransactionSerializer(ModelSerializer[Transaction]):
    account = AccountSerializer()
    invoice = InvoiceSerializer()

    class Meta:
        model = Transaction
        fields = '__all__'
