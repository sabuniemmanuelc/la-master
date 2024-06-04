from tinymce.models import HTMLField

from django.db import models

from apps.account.models import Account
from apps.service.models import Service


class Department(models.Model):
    name = models.CharField(max_length=255)
    describe = HTMLField('Describe')

    def __str__(self):
        return self.name


class Ticket(models.Model):
    class Status(models.IntegerChoices):
        TO_DO = 1, 'To Do'
        IN_PROGRESS = 2, 'In progress'
        DONE = 3, 'Done'
        CLOSE = 4, 'Close'

    class TicketRating(models.IntegerChoices):
        LIKE = 1, 'Like'
        DISLIKE = 2, 'Dislike'

    author = models.ForeignKey(
        Account, related_name='ticket_author', on_delete=models.PROTECT
    )
    assigned = models.ForeignKey(
        Account, related_name='ticket_assigned', on_delete=models.PROTECT
    )
    service = models.ForeignKey(
        Service, related_name='ticket_service', on_delete=models.PROTECT
    )
    department = models.ForeignKey(
        Department, related_name='ticket_department', on_delete=models.PROTECT
    )
    subject = models.CharField('Subject', max_length=255)
    # describe = models.TextField('Describe')
    describe = HTMLField('Describe')
    date_opened = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(
        'Ticket rating',
        choices=TicketRating.choices,
        blank=True,
        null=True,
    )
    status = models.IntegerField(
        'Ticket status',
        choices=Status.choices,
        default=Status.TO_DO,
    )

    def __str__(self):
        return self.subject


class TicketChat(models.Model):
    class TicketChatMessageRating(models.IntegerChoices):
        LIKE = 1, 'Like'
        DISLIKE = 2, 'Dislike'

    ticket = models.ForeignKey(
        Ticket, related_name='ticket_chat', on_delete=models.PROTECT
    )
    author = models.ForeignKey(
        Account, related_name='ticket_chat_author', on_delete=models.PROTECT
    )
    # message = models.TextField()
    message = HTMLField('Message')
    datetime = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(
        'Ticket chat message rating',
        choices=TicketChatMessageRating.choices,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.ticket.subject
