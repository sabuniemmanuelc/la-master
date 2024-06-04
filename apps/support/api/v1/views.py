from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.account.task import la_send_email
from apps.support.api.v1.serializers import (
    SupportFeedbackSerializer,
    TicketChatSerializer,
    TicketSerializer,
)
from apps.support.models import Ticket, TicketChat
from la import settings


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Вью для отображения тикетов."""

    queryset = Ticket.objects.all().order_by('-id')
    serializer_class = TicketSerializer


class TicketChatViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Вью для отображения тикет чатов."""

    serializer_class = TicketChatSerializer

    def get_queryset(self):
        return (
            TicketChat.objects.select_related()
            .filter(ticket__pk=self.kwargs['ticket_pk'])
            .order_by('-id')
        )


class SupportFeedbackView(APIView):
    def get_serializer(self, *args, **kwargs):
        return SupportFeedbackSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        feedback_serializer = SupportFeedbackSerializer(data=request.data)
        if feedback_serializer.is_valid(raise_exception=True):
            la_send_email.delay(
                f'Support! Message from user: {request.user.email}. Need an answer:'
                f' {"yes" if feedback_serializer.validated_data["hear_back"] else "no"}',
                feedback_serializer.validated_data['message'],
                settings.EMAIL_HOST_USER,
                'support@legal-data.tech',
            )
            return Response()
