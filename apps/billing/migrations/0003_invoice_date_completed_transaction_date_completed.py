# Generated by Django 4.1.3 on 2023-04-30 13:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('billing', '0002_remove_transaction_paid_through_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='date_completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='date_completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
