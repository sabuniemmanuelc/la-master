# Generated by Django 4.1.3 on 2023-05-01 06:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0008_remove_profile_adopted_actor_remove_profile_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='account',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='profile_account',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
