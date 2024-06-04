from django.urls import include, path

from apps.support.apps import SupportConfig

app_name = SupportConfig.name

urlpatterns = [
    path('v1/', include('apps.support.api.v1.urls', namespace='v1')),
]
