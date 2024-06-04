from django.urls import include, path

from apps.favorites.apps import FavoritesConfig

app_name = FavoritesConfig.name

urlpatterns = [
    path('v1/', include('apps.favorites.api.v1.urls', namespace='v1')),
]
