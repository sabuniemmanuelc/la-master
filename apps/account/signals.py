from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from apps.account.models import Account, LawyerEducation, Profile
from apps.account.task import la_send_email, la_send_html_email
from apps.data.models import Country, Language
from la import settings
from la.settings import DEFAULT_ACCOUNT_REAL_NAME, DEFAULT_DOMAIN


@receiver(post_save, sender=Account)
def create_profile_after_register(sender, **kwargs):
    cache.set(f'user_auth{kwargs["instance"].email}', kwargs["instance"].has_access)


@receiver(post_save, sender=Profile)
def post_save_vs(sender, instance, created, update_fields, **kwargs):
    instance.update_search_vector()


@receiver(pre_save, sender=Profile)
def create_slug(sender, instance, *args, **kwargs):
    if instance.languages:
        languages = Language.objects.filter(id__in=instance.languages).values_list(
            'value', flat=True
        )
        instance.languages_text = list(languages)
    if instance.jurisdictions:
        jurisdictions = Country.objects.filter(
            id__in=instance.jurisdictions
        ).values_list('name', flat=True)
        instance.jurisdictions_text = list(jurisdictions)
    try:
        old_verified = Profile.objects.get(id=instance.id).verified
    except Profile.DoesNotExist:
        old_verified = False
    if all((instance.verified, not old_verified)):
        la_send_html_email.delay(
            'account/templates/templated_email/profile_verified.html',
            'Your profile has just been verified!',
            {
                'username': instance.real_name
                if instance.real_name
                else DEFAULT_ACCOUNT_REAL_NAME,
                'profile_link': f'{DEFAULT_DOMAIN}/profile',
            },
            settings.EMAIL_HOST_USER,
            instance.account.email,
        )


@receiver(post_save, sender=LawyerEducation)
def send_email_message_after_fill_educations(sender, **kwargs):
    url = DEFAULT_DOMAIN + reverse(
        f'admin:{kwargs["instance"].account._meta.app_label}'
        f'_{kwargs["instance"].account._meta.model_name}_change',
        args=[kwargs["instance"].account.id],
    )
    la_send_email.delay(
        f'Support! New application for a lawyer from user: '
        f' {kwargs["instance"].account.profile_account.real_name}. {kwargs["instance"].account.email}',
        f'Login to your admin and check! URL: {url} \nEmail: {kwargs["instance"].account.email}. '
        f'User id: {kwargs["instance"].account.id}.',
        settings.EMAIL_HOST_USER,
        'support@legal-data.tech',
    )
