from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from django.urls import path

from apps.support.api.v1.views import (
    SupportFeedbackView,
    TicketChatViewSet,
    TicketViewSet,
)

app_name = 'v1'

router = DefaultRouter(trailing_slash=False)
router.register('ticket', TicketViewSet)
ticket_chat_router = NestedDefaultRouter(router, 'ticket', lookup='ticket')
ticket_chat_router.register('chat', TicketChatViewSet, basename='chat')

urlpatterns = router.urls
urlpatterns += ticket_chat_router.urls
urlpatterns += [
    path('feedback', SupportFeedbackView.as_view(), name='support_feedback'),
]
