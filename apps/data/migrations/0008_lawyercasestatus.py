# Generated by Django 4.1.3 on 2023-05-26 07:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0007_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='LawyerCaseStatus',
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
