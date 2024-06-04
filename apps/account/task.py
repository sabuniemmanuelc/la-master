import hashlib
import os
import time

import requests
from celery import shared_task

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

from la.settings import ACCESS_TOKEN, GENERAL_SLEEP_TIME, PIXEL_ID


@shared_task(serializer='json', name='send_welcome_email')
def la_send_html_email(html_template, subject, message, sender, receiver):
    time.sleep(GENERAL_SLEEP_TIME)
    html_content = render_to_string(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            html_template,
        ),
        context=message,
    ).strip()
    msg = EmailMultiAlternatives(
        subject, html_content, f'Legal Data <{sender}>', [receiver]
    )
    msg.content_subtype = 'html'
    msg.send()


@shared_task(serializer='json', name='send_email')
def la_send_email(subject, message, sender, receiver):
    time.sleep(GENERAL_SLEEP_TIME)
    msg = EmailMessage(subject, message, f'Legal Data <{sender}>', [receiver])
    msg.send()


@shared_task(serializer='json', name='send_meta_pixel_event')
def send_meta_pixel_event(client_email: str, client_ip: str) -> None:
    """Отправка события в Meta Pixel после регистрации пользователя."""
    time.sleep(GENERAL_SLEEP_TIME)
    email_hashed = hashlib.sha256(client_email.encode('utf-8')).hexdigest()

    meta_url = f'https://graph.facebook.com/v17.0/{PIXEL_ID}/events'

    event_data = {
        'event_name': 'CompleteRegistration',
        'event_time': int(time.time()),
        'user_data': {'em': [email_hashed], 'client_ip_address': client_ip},
        'custom_data': {},
        'event_source_url': 'https://legaldata.ltd/',
        'action_source': 'website',
    }

    requests.post(meta_url, json={'data': [event_data], 'access_token': ACCESS_TOKEN})
