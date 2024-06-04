from django.apps import AppConfig


class BillingConfig(AppConfig):
    """Config app billing"""

    name = 'apps.billing'

    def ready(self):
        pass
