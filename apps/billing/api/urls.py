from django.urls import include, path

from apps.billing.apps import BillingConfig

app_name = BillingConfig.name

urlpatterns = [
    path('v1/', include('apps.billing.api.v1.urls', namespace='v1')),
]
