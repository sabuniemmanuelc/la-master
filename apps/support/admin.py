import datetime

from django_admin_inline_paginator.admin import TabularInlinePaginated
from rangefilter.filters import DateRangeFilter

from django.contrib import admin

from apps.support.models import Department, Ticket, TicketChat


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'describe')
    search_fields = ('name', 'describe')


class TicketChatInline(TabularInlinePaginated):
    model = TicketChat
    per_page = 5
    readonly_fields = ('author', 'rating')
    raw_id_fields = ('author',)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            return []
        return self.readonly_fields


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'subject',
        'author',
        'assigned',
        'service',
        'department',
        'describe',
        'date_opened',
        'date_updated',
        'rating',
        'status',
    )
    list_filter = (
        ('date_opened', DateRangeFilter),
        ('date_updated', DateRangeFilter),
        'status',
        'rating',
    )
    search_fields = (
        'author__email',
        'assigned__email',
        'service__name',
        'department__name',
        'subject',
        'describe',
        'date_opened',
        'date_updated',
        'rating',
        'status',
    )
    readonly_fields = ('author', 'rating')
    list_select_related = ('author', 'assigned', 'service', 'department')
    raw_id_fields = ('author', 'assigned', 'service', 'department')

    def get_rangefilter_date_opened_default(self, request):
        return datetime.date.today, datetime.date.today

    def get_rangefilter_date_updated_default(self, request):
        return datetime.date.today, datetime.date.today

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            return []
        return self.readonly_fields

    def get_queryset(self, request):
        filter_dict = {}
        if not request.user.is_admin:
            filter_dict['assigned'] = request.user
        return (
            super()
            .get_queryset(request)
            .select_related(
                'author',
                'assigned',
                'service',
                'department',
            )
            .filter(**filter_dict)
        )

    inlines = [
        TicketChatInline,
    ]

    def save_formset(self, request, form, formset, change):
        for inline_form in formset.forms:
            if inline_form.has_changed():
                if not inline_form.instance.author_id:
                    inline_form.instance.author_id = request.user.id
        super().save_formset(request, form, formset, change)


@admin.register(TicketChat)
class TicketChatAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'message', 'datetime', 'rating')
    list_filter = (
        ('datetime', DateRangeFilter),
        'rating',
    )
    search_fields = (
        'ticket__subject',
        'author__email',
        'message',
        'datetime',
        'rating',
    )
    readonly_fields = ('author', 'rating')
    list_select_related = ('ticket', 'author')
    raw_id_fields = ('ticket', 'author')

    def get_rangefilter_datetime_default(self, request):
        return datetime.date.today, datetime.date.today

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            return []
        return self.readonly_fields

    def get_queryset(self, request):
        filter_dict = {}
        if not request.user.is_admin:
            filter_dict['ticket__assigned'] = request.user
        return (
            super()
            .get_queryset(request)
            .select_related('author', 'ticket')
            .filter(**filter_dict)
        )
