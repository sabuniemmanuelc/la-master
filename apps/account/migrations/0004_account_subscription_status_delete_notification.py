# Generated by Django 4.1.3 on 2023-04-26 08:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0003_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='subscription_status',
            field=models.IntegerField(
                choices=[(1, 'Subscription'), (2, 'Trial')],
                default=2,
                verbose_name='Subscription status',
            ),
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
