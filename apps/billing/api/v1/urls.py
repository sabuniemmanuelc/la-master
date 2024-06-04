from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from django.urls import path

from apps.billing.api.v1.views import (
    CheckoutSessionEmailView,
    CheckoutSessionView,
    CheckoutWebHookView,
    DownloadInvoiceView,
    InvoiceViewSet,
    TransactionViewSet,
)

app_name = 'v1'

router = DefaultRouter(trailing_slash=False)
router.register('invoice', InvoiceViewSet, basename='invoice')
transaction_router = NestedDefaultRouter(router, 'invoice', lookup='invoice')
transaction_router.register('transaction', TransactionViewSet, basename='transaction')

urlpatterns = router.urls
urlpatterns += transaction_router.urls

urlpatterns += [
    path('checkout/webhook', CheckoutWebHookView.as_view(), name='checkout_webhook'),
    path(
        'checkout/<int:invoice_id>',
        CheckoutSessionView.as_view(),
        name='checkout_session_view',
    ),
    path(
        'checkout/<str:hash_invoice_id>',
        CheckoutSessionEmailView.as_view(),
        name='checkout_session_email_view',
    ),
    path(
        'download/invoice/<str:date_created>/<str:invoice_id>',
        DownloadInvoiceView.as_view(),
        name='download_invoice',
    ),
]
