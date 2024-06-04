from rest_framework import routers

from django.urls import re_path as url

from apps.notification.api.v1.views import (
    AllNotification,
    AllNotificationCount,
    MarkAllAsRead,
    MarkAsRead,
    MarkAsUnread,
    NotificationViewSet,
    UnreadNotificationCount,
    UnreadNotificationsList,
)
from apps.notification.apps import NotificationConfig

router = routers.DefaultRouter()
router.register('', NotificationViewSet)

app_name = NotificationConfig.name

urlpatterns = [
    url(r'^all/', AllNotification.as_view({'get': 'list'}), name='notification_all'),
    url(
        r'^unread/',
        UnreadNotificationsList.as_view({'get': 'list'}),
        name='notification_unread',
    ),
    url(
        r'^mark-all-as-read/$',
        MarkAllAsRead.as_view(),
        name='notification_mark_all_as_read',
    ),
    url(
        r'^mark-as-read/(?P<id>\d+)/$',
        MarkAsRead.as_view(),
        name='notification_mark_as_read',
    ),
    url(
        r'^mark-as-unread/(?P<id>\d+)/$',
        MarkAsUnread.as_view(),
        name='notification_mark_as_unread',
    ),
    # url(r'^delete/(?P<id>\d+)/$', Delete.as_view(), name='notification_delete'),
    url(
        r'^unread-count/$',
        UnreadNotificationCount.as_view(),
        name='notification_live_unread_notification_count',
    ),
    url(
        r'^all-count/$',
        AllNotificationCount.as_view(),
        name='notification_live_all_notification_count',
    ),
    url(
        r'^unread-list/$',
        UnreadNotificationsList.as_view({'get': 'list'}),
        name='notification_live_unread_notification_list',
    ),
]
