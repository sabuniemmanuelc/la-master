# Generated by Django 4.1.3 on 2023-05-25 07:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0006_rename_departments_department_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
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
