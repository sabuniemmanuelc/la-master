from datetime import timedelta

import pytz
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_simplejwt import authentication

from django.utils import timezone

from apps.account.models import Account
from la.settings import (
    ACCESS_APPS_WITHOUT_PAY,
    SUBSCRIPTION_PERIOD_DAYS,
    TRIAL_PERIOD_DAYS,
)


class CheckPaymentRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            user = authentication.JWTAuthentication().authenticate(request)
        except Exception as e:
            print(e)
        else:
            if user is not None:
                user = user[0]
                if all(
                    (
                        user.subscription_status
                        == Account.SubscriptionStatus.TRIAL.value,
                        user.date_joined + timedelta(days=TRIAL_PERIOD_DAYS)
                        > timezone.now(),
                        request.resolver_match.app_name not in ACCESS_APPS_WITHOUT_PAY,
                    )
                ):
                    response = Response(
                        data='Payment is required to access this resource.',
                        status=status.HTTP_402_PAYMENT_REQUIRED,
                    )
                elif all(
                    (
                        user.subscription_status
                        == Account.SubscriptionStatus.SUBSCRIPTION.value,
                        request.resolver_match.app_name not in ACCESS_APPS_WITHOUT_PAY,
                    )
                ):
                    if user.last_subscription_payment_date is None:
                        response = Response(
                            data='Bad request.',
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    elif (
                        user.last_subscription_payment_date
                        + timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
                        > timezone.now()
                    ):
                        response = Response(
                            data='Payment is required to access this resource.',
                            status=status.HTTP_402_PAYMENT_REQUIRED,
                        )
                else:
                    return response
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                response.render()
        return response


class TimezoneMiddleware(object):
    """
    Middleware to properly handle the users timezone
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            tz_str = request.user.profile.timezone
            timezone.activate(pytz.timezone(tz_str))
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
