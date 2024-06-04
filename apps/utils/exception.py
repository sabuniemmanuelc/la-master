from rest_framework import status
from rest_framework.exceptions import APIException


class PaymentRequired(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_code = 'payment_required'
    default_detail = 'Payment is required to access this resource.'
