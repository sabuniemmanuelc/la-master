from model_utils import Choices
from notifications.base.models import AbstractNotification

from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(AbstractNotification):
    LEVELS = Choices(
        'success', 'info', 'warning', 'error', 'paid', 'unpaid', 'canceled'
    )
    level = models.CharField(
        _('level'), choices=LEVELS, default=LEVELS.info, max_length=20, db_index=True
    )

    class Meta(AbstractNotification.Meta):
        abstract = False
