from django.db import models


class SearchHistoryItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    account_id = models.BigIntegerField()
    entity_name = models.CharField(max_length=255)
    search_parameters = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField()
    items_found_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'search_history_items'
