# Generated by Django 4.1.3 on 2023-07-18 16:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0014_alter_gender_options_gender_my_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('value', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
