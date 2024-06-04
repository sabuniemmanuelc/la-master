import hashlib
import uuid

from notifications.base.models import AbstractNotification  # noqa: F401

from django.contrib.auth.base_user import (  # noqa: F401
    AbstractBaseUser,
    BaseUserManager,
)
from django.contrib.auth.models import AbstractUser, PermissionsMixin  # noqa: F401
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models

from apps.data.models import AdoptedActor  # noqa: F401
from apps.data.models import AlmaMater  # noqa: F401
from apps.data.models import Date  # noqa: F401
from apps.data.models import Department  # noqa: F401
from apps.data.models import Document  # noqa: F401
from apps.data.models import HearFromUs  # noqa: F401
from apps.data.models import Jurisdiction  # noqa: F401
from apps.data.models import Language  # noqa: F401
from apps.data.models import LawyerSpecialization  # noqa: F401
from apps.data.models import Sector  # noqa: F401
from apps.data.models import (
    City,
    Country,
    Degree,
    EmploymentType,
    Expertise,
    FileUpload,
    Gender,
    LawyerArea,
    LawyerCaseStatus,
    LawyerSource,
    Practice,
    Profession,
)
from apps.service.models import Service


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Account(AbstractUser):
    class SubscriptionStatus(models.IntegerChoices):
        TRIAL = 1, 'Trial'
        SUBSCRIPTION = 2, 'Subscription'

    username = models.CharField('Username', blank=True, max_length=150)
    email = models.EmailField('Email', max_length=255, unique=True)
    is_admin = models.BooleanField('Is admin', default=False)
    services = models.ManyToManyField(
        Service,
        through='AccountServiceThrough',
        related_name='account_services',
        blank=True,
    )
    balance = models.DecimalField('Balance', default=0, max_digits=10, decimal_places=2)
    subscription_status = models.IntegerField(
        'Subscription status',
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIAL,
    )
    last_subscription_payment_date = models.DateTimeField(
        'Last subscription payment date', blank=True, null=True
    )
    has_access = models.BooleanField('Has access', default=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class AccountServiceThrough(models.Model):
    account = models.ForeignKey(
        Account,
        related_name='account_service_through_account',
        on_delete=models.PROTECT,
    )
    service = models.ForeignKey(
        Service,
        related_name='account_service_through_service',
        on_delete=models.PROTECT,
    )
    date_activated = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return (
            f'{self.account.email}/{self.service.name}/'
            f'{self.date_activated.strftime("%m/%d/%Y, %H:%M:%S")}'
        )


def user_upload_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    hash_string = hashlib.md5(
        f'{instance.account.email}{instance.account.date_joined}{instance.account.id}'.encode()
    ).hexdigest()
    return f'avatars/{hash_string}/{filename}'


class Profile(models.Model):
    account = models.OneToOneField(
        Account, related_name='profile_account', on_delete=models.CASCADE
    )
    avatar = models.ForeignKey(
        FileUpload,
        related_name='profile_avatar',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        verbose_name='Phone number',
        null=True,
        blank=True,
        max_length=100,
    )
    auto_withdraw_balance_funds = models.BooleanField(
        'Withdraw from balance funds', default=False
    )
    date_created = models.DateTimeField(auto_now_add=True)
    country = models.ForeignKey(
        Country,
        related_name='profile_country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        related_name='profile_city',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    profession = models.ForeignKey(
        Profession,
        related_name='profile_profession',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    practice = models.ForeignKey(
        Practice,
        related_name='profile_practice',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    expertise = models.ManyToManyField(
        Expertise, related_name='profile_expertise', blank=True, null=True
    )
    gender = models.ForeignKey(
        Gender,
        blank=True,
        null=True,
        related_name='profile_gender',
        on_delete=models.SET_NULL,
    )
    birthday = models.DateField('Birthday', blank=True, null=True)
    first_name = models.CharField('First name', max_length=255, blank=True)
    last_name = models.CharField('Last name', max_length=255, blank=True)
    place_work = models.CharField('Place of work', max_length=255, blank=True)
    key_cases = models.TextField('Key cases', blank=True)
    real_name = models.CharField('Real name', max_length=255, blank=True)
    description = models.TextField('Description', blank=True, db_index=True)
    verified = models.BooleanField('Verified', default=False)
    rate = models.DecimalField(
        'Rate', blank=True, null=True, max_digits=10, decimal_places=2
    )
    experience_description = models.TextField('Experience description', blank=True)
    search_visibility = models.BooleanField('Search visibility', default=True)
    phone_visibility = models.BooleanField('Phone visibility', default=True)
    online_visibility = models.BooleanField('Online visibility', default=True)
    interests = models.JSONField('Interests', default=list, blank=True, null=True)
    specializations = models.JSONField(
        'Specializations', default=list, blank=True, null=True
    )
    jurisdictions = models.JSONField(
        'Jurisdictions', default=list, blank=True, null=True
    )
    jurisdictions_text = models.JSONField(
        'Jurisdictions text', default=list, blank=True, null=True
    )
    languages = models.JSONField('Languages', default=list, blank=True, null=True)
    languages_text = models.JSONField(
        'Languages text', default=list, blank=True, null=True
    )
    # Контакты
    mobile_phone_number = models.CharField(
        'Mobile phone number',
        blank=True,
        max_length=255,
    )
    email = models.EmailField('Email', max_length=255, blank=True)
    address = models.CharField('Address', max_length=255, blank=True)
    work_phone_number = models.CharField(
        'Work phone number',
        blank=True,
        max_length=255,
    )
    website = models.CharField('Website', max_length=255, blank=True)
    instagram = models.CharField('Instagram', max_length=255, blank=True)
    facebook = models.CharField('Facebook', max_length=255, blank=True)
    linkedin = models.CharField('Linkedin', max_length=255, blank=True)
    telegram = models.CharField('Telegram', max_length=255, blank=True)
    whatsapp = models.CharField('Whatsapp', max_length=255, blank=True)
    twitter = models.CharField('Twitter', max_length=255, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    sending_notifications = models.BooleanField('Sending notifications', default=False)
    sending_browser_notifications = models.BooleanField(
        'Sending browser notifications', default=False
    )

    class Meta:
        indexes = [
            GinIndex(
                fields=[
                    "search_vector",
                ]
            ),
        ]

    def update_search_vector(self):
        qs = Profile.objects.filter(pk=self.pk)
        qs.update(
            search_vector=SearchVector('real_name')
            + SearchVector('description')
            + SearchVector('experience_description')
            + SearchVector('rate')
        )

    def __str__(self):
        return self.account.email


def user_upload_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    hash_string = hashlib.md5(
        f'{instance.account.email}{instance.account.date_joined}{instance.account.id}'.encode()
    ).hexdigest()
    return f'files/decisions/{hash_string}/{filename}'


class LawyerCase(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_case_account', on_delete=models.CASCADE
    )
    title = models.CharField('Title', max_length=255, blank=True)
    client_name = models.CharField('Client name', max_length=255, blank=True)
    project_description = models.TextField('Project description', blank=True)
    service_description = models.TextField('Service description', blank=True)
    impact = models.TextField('Impact', blank=True)
    status = models.ForeignKey(
        LawyerCaseStatus,
        related_name='lawyer_case_status',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    jurisdiction = models.ForeignKey(
        Country,
        related_name='lawyer_case_jurisdiction',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    decision_link = models.CharField('Decision link', max_length=255, blank=True)
    decision = models.ForeignKey(
        FileUpload,
        related_name='lawyer_case_decision',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


class Specialization(models.Model):
    account = models.ForeignKey(
        Account, related_name='specialization_account', on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Interest(models.Model):
    account = models.ForeignKey(
        Account, related_name='interests_account', on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Contact(models.Model):
    account = models.ForeignKey(
        Account, related_name='contact_account', on_delete=models.CASCADE
    )
    mobile_phone_number = models.CharField(
        verbose_name='Mobile phone number',
        null=True,
        blank=True,
        max_length=100,
    )
    email = models.EmailField('Email', max_length=255, blank=True)
    address = models.CharField('Address', max_length=255, blank=True)
    work_phone_number = models.CharField(
        verbose_name='Work phone number',
        null=True,
        blank=True,
        max_length=100,
    )
    website = models.CharField('Website', max_length=255, blank=True)
    instagram = models.CharField('Instagram', max_length=255, blank=True)
    facebook = models.CharField('Facebook', max_length=255, blank=True)
    linkedin = models.CharField('Linkedin', max_length=255, blank=True)
    telegram = models.CharField('Telegram', max_length=255, blank=True)
    whatsapp = models.CharField('Whatsapp', max_length=255, blank=True)
    twitter = models.CharField('Twitter', max_length=255, blank=True)

    def __str__(self):
        return self.account.email


class AdditionalLanguages(models.Model):
    account = models.ForeignKey(
        Account, related_name='additional_languages_account', on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class LawyerService(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_service_account', on_delete=models.CASCADE
    )
    title = models.CharField('Title', max_length=255, blank=True)
    price = models.DecimalField(
        'Price', blank=True, null=True, max_digits=10, decimal_places=2
    )
    description = models.TextField('Description', blank=True)

    def __str__(self):
        return self.account.email


class LawyerExperience(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_experience_account', on_delete=models.CASCADE
    )
    country = models.ForeignKey(
        Country,
        related_name='lawyer_experience_country',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    city = models.ForeignKey(
        City,
        related_name='lawyer_experience_city',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    company_name = models.CharField('Company name', max_length=255, blank=True)
    position = models.CharField('Position', max_length=255, blank=True)
    employment_type = models.ForeignKey(
        EmploymentType,
        related_name='employment_type_account',
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField('Start date')
    end_date = models.DateTimeField('End date', blank=True, null=True)
    still_here = models.BooleanField('Still here', default=False)
    description = models.TextField('Description', blank=True)

    def __str__(self):
        return self.account.email


def user_upload_diploma_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    hash_string = hashlib.md5(
        f'{instance.account.email}{instance.account.date_joined}{instance.account.id}'.encode()
    ).hexdigest()
    return f'files/diplomas/{hash_string}/{filename}'


class LawyerEducation(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_education_account', on_delete=models.CASCADE
    )
    degree = models.ForeignKey(
        Degree, related_name='lawyer_education_degree', on_delete=models.CASCADE
    )
    specialization = models.CharField(max_length=255, blank=True)
    university_name = models.CharField('University name', max_length=255, blank=True)
    license_id = models.CharField('License id', max_length=255, blank=True)
    country = models.ForeignKey(
        Country,
        related_name='lawyer_education_country',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    city = models.ForeignKey(
        City,
        related_name='lawyer_education_city',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField('Start date')
    end_date = models.DateTimeField('End date', blank=True, null=True)
    still_here = models.BooleanField('Still here', default=False)
    description = models.TextField('Description', blank=True)
    id_diploma = models.CharField('Diploma id', max_length=255, blank=True)
    diploma = models.ForeignKey(
        FileUpload,
        related_name='lawyer_education_diploma',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.university_name


def user_upload_award_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    hash_string = hashlib.md5(
        f'{instance.account.email}{instance.account.date_joined}{instance.account.id}'.encode()
    ).hexdigest()
    return f'files/awards/{hash_string}/{filename}'


class LawyerAward(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_award_account', on_delete=models.CASCADE
    )
    title = models.CharField('Title', max_length=255, blank=True)
    organisation = models.CharField('Organisation', max_length=255, blank=True)
    issue_date = models.DateTimeField('Issue date')
    award = models.ForeignKey(
        FileUpload,
        related_name='lawyer_award_award',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.account.email


class LawyerPublication(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_publication_account', on_delete=models.CASCADE
    )
    media = models.CharField('Media', max_length=255, blank=True)
    title = models.CharField('Title', max_length=255)
    date = models.DateTimeField('Date')
    link = models.CharField('Link', max_length=255, blank=True)
    description = models.TextField('Description', blank=True)

    def __str__(self):
        return self.account.email


class LawyerPublicActivity(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_public_activity_account', on_delete=models.CASCADE
    )
    organisation = models.CharField('Organisation', max_length=255, blank=True)
    role = models.CharField('Role', max_length=255, blank=True)
    country = models.ForeignKey(
        Country,
        related_name='lawyer_public_activity_country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        related_name='lawyer_public_activity_city',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField('Start date', blank=True, null=True)
    end_date = models.DateTimeField('End date', blank=True, null=True)
    still_here = models.BooleanField('Still here', default=False)
    description = models.TextField('Description', blank=True)

    def __str__(self):
        return self.account.email


class LawyerRating(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_rating_account', on_delete=models.CASCADE
    )
    source = models.ForeignKey(
        LawyerSource, related_name='lawyer_rating_source', on_delete=models.CASCADE
    )
    area = models.ForeignKey(
        LawyerArea, related_name='lawyer_rating_area', on_delete=models.CASCADE
    )
    credential = models.CharField('Credential', max_length=255, blank=True)

    def __str__(self):
        return self.account.email


def user_upload_license_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    hash_string = hashlib.md5(
        f'{instance.account.email}{instance.account.date_joined}{instance.account.id}'.encode()
    ).hexdigest()
    return f'files/licenses/{hash_string}/{filename}'


class LawyerLicense(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_license_account', on_delete=models.CASCADE
    )
    title = models.CharField('Title', max_length=255, blank=True)
    issuing_organisation = models.CharField(
        'Issuing organisation', max_length=255, blank=True
    )
    country = models.ForeignKey(
        Country,
        related_name='lawyer_license_country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        related_name='lawyer_license_city',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    credential_id = models.CharField('Credential', max_length=255, blank=True)
    issue_date = models.DateTimeField('Issue date')
    expiration_date = models.DateTimeField('Expiration date', blank=True, null=True)
    infinite = models.BooleanField('Infinite', default=False)
    license_file = models.ForeignKey(
        FileUpload,
        related_name='lawyer_license_license_file',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.account.email


class LawyerJurisdictions(models.Model):
    account = models.ForeignKey(
        Account, related_name='lawyer_jurisdictions_account', on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value
