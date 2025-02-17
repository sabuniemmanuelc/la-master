# Generated by Django 4.1.3 on 2022-12-26 08:37

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
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
                (
                    'invoice_id',
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, verbose_name='Invoice id'
                    ),
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                (
                    'due_date',
                    models.DateTimeField(
                        blank=True, null=True, verbose_name='Due date'
                    ),
                ),
                (
                    'paid_status',
                    models.IntegerField(
                        choices=[(1, 'Paid'), (2, 'Unpaid'), (3, 'Canceled')],
                        default=2,
                        verbose_name='Paid status',
                    ),
                ),
                (
                    'discount',
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name='Discount',
                    ),
                ),
                (
                    'account',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='invoice_account',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'service',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='invoice_service',
                        to='service.service',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
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
                (
                    'transaction_id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        verbose_name='Transaction id',
                    ),
                ),
                (
                    'paid_through',
                    models.CharField(
                        default='Super Card System',
                        max_length=255,
                        verbose_name='Paid Through',
                    ),
                ),
                (
                    'describe',
                    models.CharField(
                        default='Invoice Payment',
                        max_length=255,
                        verbose_name='Describe',
                    ),
                ),
                (
                    'sum',
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name='Sum'
                    ),
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                (
                    'account',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='transaction_account',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'invoice',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='transaction_invoice',
                        to='billing.invoice',
                    ),
                ),
            ],
        ),
    ]
