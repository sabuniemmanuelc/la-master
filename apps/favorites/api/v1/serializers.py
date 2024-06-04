from rest_framework import serializers

from apps.favorites.models import Favorites


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = ['account', 'search_id']
