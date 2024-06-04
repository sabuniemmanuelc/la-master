from django.urls import include, path

from apps.data.apps import DataConfig

app_name = DataConfig.name

urlpatterns = [
    path('v1/', include('apps.data.api.v1.urls', namespace='v1')),
]
