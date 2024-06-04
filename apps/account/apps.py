from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Config app account"""

    name = 'apps.account'

    def ready(self):
        from . import signals  # noqa: F401
