import datetime

from django_admin_inline_paginator.admin import TabularInlinePaginated
from rangefilter.filters import DateRangeFilter, NumericRangeFilter

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.account.models import Account, AccountServiceThrough, LawyerEducation, Profile


class LawyerEducationInline(TabularInlinePaginated):
    model = LawyerEducation
    fields = [
        'degree',
        'specialization',
        'university_name',
        'license_id',
        'country',
        'city',
        'start_date',
        'end_date',
        'still_here',
        'id_diploma',
        'diploma',
    ]
    extra = 0
    list_select_related = ('country', 'city')
    raw_id_fields = ('country', 'city')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(
            set(
                [field.name for field in self.opts.local_fields]
                + [field.name for field in self.opts.local_many_to_many]
            )
        )

        if 'is_submitted' in readonly_fields:
            readonly_fields.remove('is_submitted')

        return readonly_fields

    class Meta:
        ordering = ['id']


@admin.register(Account)
class AccountAdmin(BaseUserAdmin):
    inlines = [
        LawyerEducationInline,
    ]

    list_display = (
        'email',
        'account_full_name',
        'date_joined',
        'is_active',
        'account_services',
        'balance',
        'has_access',
    )
    list_filter = (
        ('date_joined', DateRangeFilter),
        ('balance', NumericRangeFilter),
    )
    search_fields = ('email', 'date_joined', 'balance')
    fieldsets = (
        (None, {'fields': ('date_joined', 'email', 'password', 'has_access')}),
        # ('Personal info', {'fields': ()}),
        (
            'Permissions',
            {
                'fields': (
                    'is_admin',
                    'is_active',
                    'is_staff',
                    'groups',
                    'user_permissions',
                )
            },
        ),
    )

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
    )
    ordering = ('email',)
    filter_horizontal = ()

    def get_rangefilter_date_joined_default(self, request):
        return datetime.date.today, datetime.date.today

    @admin.display(
        description='services',
        empty_value='-',
    )
    def account_services(self, account):
        return ','.join(account.services.values_list('name', flat=True))

    @admin.display(
        description='Full name',
        empty_value='-',
    )
    def account_full_name(self, account):
        return account.profile_account.real_name

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('services')


@admin.register(LawyerEducation)
class LawyerEducationAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'degree',
        'specialization',
        'university_name',
        'license_id',
        'country',
        'city',
        'start_date',
        'end_date',
        'still_here',
        'id_diploma',
    )
    list_filter = (
        ('start_date', DateRangeFilter),
        ('end_date', DateRangeFilter),
    )
    search_fields = (
        'account',
        'degree',
        'specialization',
        'university_name',
        'license_id',
        'country__name',
        'city__name',
        'start_date',
        'end_date',
        'id_diploma',
    )
    list_select_related = ('account', 'country', 'city')
    raw_id_fields = ('account', 'country', 'city')

    def get_rangefilter_start_date_default(self, request):
        return datetime.date.today, datetime.date.today

    def get_rangefilter_end_date_default(self, request):
        return datetime.date.today, datetime.date.today


@admin.register(Profile)
class AccountProfileAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'phone_number',
        'auto_withdraw_balance_funds',
        'date_created',
        'birthday',
        'gender',
        'country',
        'city',
    )
    list_filter = ('gender',)
    search_fields = ('account__email', 'phone_number', 'date_created', 'gender__value')
    list_select_related = ('account', 'gender', 'country', 'city')
    raw_id_fields = ('account', 'gender', 'country', 'city')


@admin.register(AccountServiceThrough)
class AccountServiceThroughAdmin(admin.ModelAdmin):
    list_display = ('account', 'service', 'date_activated', 'enabled')
    list_filter = (('date_activated', DateRangeFilter),)
    search_fields = ('account__email', 'service__name', 'date_activated')
    list_select_related = ('account', 'service')
    raw_id_fields = ('account', 'service')

    def get_rangefilter_date_joined_default(self, request):
        return datetime.date.today, datetime.date.today
