from django.urls import include, path

from apps.account.apps import AccountsConfig

app_name = AccountsConfig.name

urlpatterns = [
    path('v1/', include('apps.account.api.v1.urls', namespace='v1')),
]
