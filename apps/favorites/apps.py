from django.apps import AppConfig


class FavoritesConfig(AppConfig):
    """Favorites app account"""

    name = 'apps.favorites'

    def ready(self):
        pass
