from django.apps import AppConfig


class NotificationConfig(AppConfig):
    """Config app notification"""

    name = 'apps.notification'

    def ready(self):
        pass
