# Generated by Django 4.1.3 on 2023-06-10 11:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0029_remove_profile_additional_languages'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='additional_languages',
            field=models.JSONField(default=list, verbose_name='Additional languages'),
        ),
    ]
