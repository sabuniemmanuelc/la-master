from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from la import settings


class Command(BaseCommand):
    help = 'Creates the MR_ROBOT account'

    def handle(self, *args, **options):
        settings.MR_ROBOT_ACCOUNT = get_user_model().objects.get_or_create(
            email='mr_robot@legal-data.tech',
            is_admin=True,
            is_staff=True,
        )
