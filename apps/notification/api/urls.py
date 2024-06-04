from django.urls import include, path

from apps.notification.apps import NotificationConfig

app_name = NotificationConfig.name

urlpatterns = [
    path('v1/', include('apps.notification.api.v1.urls', namespace='v1')),
]
