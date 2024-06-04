from notifications.signals import notify

from django.contrib.auth import get_user_model

from apps.account.models import Account, Profile

MR_ROBOT_ACCOUNT = get_user_model().objects.get(email='mr_robot@legal-data.tech')


def send_notification_if_applicable(
    recipient: Account, message: str, level: str | None = None
) -> bool:
    """
    Проверяет, нужно ли отправлять уведомление пользователю на основе флага "sending_notifications"
    в его профиле и отправляет уведомление, если это необходимо.

    :param recipient: экземпляр класса Account
    :param message: текст уведомления
    :param level: левел уведомления
    :return: boolean (True если отправляем уведомление, False если нет)
    """
    try:
        profile = recipient.profile_account
        if profile.sending_notifications:
            notify.send(
                MR_ROBOT_ACCOUNT,
                recipient=recipient,
                verb=message,
                level=level if level else 'info',
            )
            return True
    except Profile.DoesNotExist:
        pass
    return False
