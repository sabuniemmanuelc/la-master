from tinymce.models import HTMLField

from django.db import models


class Service(models.Model):
    name = models.CharField('Name', max_length=255, unique=True)
    cost = models.DecimalField('Cost', max_digits=10, decimal_places=2)
    describe = HTMLField('Describe', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField('Enabled', default=True)
    amount_days = models.IntegerField('Amount days', default=31)

    def __str__(self):
        return self.name
