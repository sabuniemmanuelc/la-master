import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la.settings')
app = Celery('laCelery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'every': {
        'task': 'apps.billing.tasks.create_invoice_payment_background',
        'schedule': crontab(minute='*/5'),
    },
    'check_transaction_status_background': {
        'task': 'apps.billing.tasks.check_transaction_status_background',
        'schedule': crontab(minute='0'),
    },
    'send_invoice_payment_email_background': {
        'task': 'apps.billing.tasks.send_invoice_payment_email_background',
        'schedule': crontab(minute='*/5'),
    },
}
app.autodiscover_tasks()
