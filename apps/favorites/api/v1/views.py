from rest_framework.viewsets import ModelViewSet

from apps.favorites.api.v1.serializers import FavoritesSerializer
from apps.favorites.models import Favorites


class FavoritesViewset(ModelViewSet):
    queryset = Favorites.objects.all()
    serializer_class = FavoritesSerializer
