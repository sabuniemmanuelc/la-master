from django.urls import include, path

from apps.service.apps import ServiceConfig

app_name = ServiceConfig.name

urlpatterns = [
    path('v1/', include('apps.service.api.v1.urls', namespace='v1')),
]
