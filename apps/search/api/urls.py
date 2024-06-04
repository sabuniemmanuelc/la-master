from django.urls import include, path

from apps.search.apps import SearchConfig

app_name = SearchConfig.name

urlpatterns = [
    path('v1/', include('apps.search.api.v1.urls', namespace='v1')),
]
