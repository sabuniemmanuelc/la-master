from django.db import models

from apps.account.models import Account


class Favorites(models.Model):
    account = models.ForeignKey(
        Account, related_name='favorites_account', on_delete=models.CASCADE
    )
    search_id = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return f'{self.account.email} / {self.search_id}'
