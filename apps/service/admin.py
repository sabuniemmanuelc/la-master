import datetime

from rangefilter.filters import DateRangeFilter, NumericRangeFilter

from django.contrib import admin

from apps.service.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cost',
        'describe',
        'date_created',
        'enabled',
        'amount_days',
    )
    list_filter = (
        ('date_created', DateRangeFilter),
        ('cost', NumericRangeFilter),
        ('amount_days', NumericRangeFilter),
    )
    search_fields = ('name', 'cost', 'describe', 'date_created', 'amount_days')

    def get_rangefilter_date_created_default(self, request):
        return datetime.date.today, datetime.date.today
