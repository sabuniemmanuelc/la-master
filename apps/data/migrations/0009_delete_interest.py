# Generated by Django 4.1.3 on 2023-05-26 11:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0017_remove_profile_interest'),
        ('data', '0008_lawyercasestatus'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Interest',
        ),
    ]
