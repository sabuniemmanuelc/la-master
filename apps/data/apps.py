from django.apps import AppConfig


class DataConfig(AppConfig):
    """Data app account"""

    name = 'apps.data'

    def ready(self):
        pass
