# Generated by Django 4.1.3 on 2023-06-21 14:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0014_alter_gender_options_gender_my_order'),
        ('account', '0050_lawyereducation_license_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='Birthday'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='expertise',
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name='profile_expertise',
                to='data.expertise',
            ),
        ),
    ]
