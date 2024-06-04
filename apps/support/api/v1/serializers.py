from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.account.api.v1.serializers import AccountSerializer
from apps.service.api.v1.serializers import ServiceSerializer
from apps.support.models import Department, Ticket, TicketChat


class DepartmentSerializer(ModelSerializer[Ticket]):
    class Meta:
        ref_name = 'DepartmentSerializer'
        model = Department
        fields = [
            'name',
            'describe',
        ]


class TicketSerializer(ModelSerializer[Ticket]):
    """Сериализатор тикетов."""

    author = AccountSerializer()
    assigned = AccountSerializer()
    service = ServiceSerializer()
    department = DepartmentSerializer()

    class Meta:
        ref_name = 'TicketSerializer'
        model = Ticket
        fields = [
            'author',
            'assigned',
            'service',
            'department',
            'subject',
            'describe',
            'date_opened',
            'date_updated',
            'rating',
            'status',
        ]


class TicketChatSerializer(ModelSerializer[TicketChat]):
    """Сериализатор чата тикетов."""

    ticket = TicketSerializer()
    author = AccountSerializer()

    class Meta:
        ref_name = 'TicketChatSerializer'
        model = TicketChat
        fields = [
            'ticket',
            'author',
            'message',
            'datetime',
            'rating',
        ]


class SupportFeedbackSerializer(serializers.Serializer):
    message = serializers.CharField()
    hear_back = serializers.BooleanField()
