# Generated by Django 4.1.3 on 2023-04-27 07:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0007_profile_adopted_actor_profile_date_and_more'),
        ('data', '0005_adoptedactor_date_departments_documents_jurisdiction_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Departments',
            new_name='Department',
        ),
        migrations.RenameModel(
            old_name='Documents',
            new_name='Document',
        ),
    ]
