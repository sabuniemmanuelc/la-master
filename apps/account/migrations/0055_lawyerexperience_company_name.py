# Generated by Django 4.1.3 on 2023-07-02 10:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0054_lawyerexperience_city_lawyerexperience_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawyerexperience',
            name='company_name',
            field=models.CharField(
                blank=True, max_length=255, verbose_name='Company name'
            ),
        ),
    ]
