# Generated by Django 4.1.3 on 2023-05-26 11:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0016_specialization'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='interest',
        ),
    ]
