# Generated by Django 4.1.3 on 2022-12-28 18:13

import tinymce.models

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='describe',
            field=tinymce.models.HTMLField(verbose_name='Describe'),
        ),
    ]
