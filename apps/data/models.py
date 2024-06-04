import hashlib
import os
import uuid

import cities_light
from cities_light import ICity
from cities_light.abstract_models import (
    AbstractCity,
    AbstractCountry,
    AbstractRegion,
    AbstractSubRegion,
    ToSearchTextField,
)
from cities_light.receivers import connect_default_signals

from django.contrib.postgres.indexes import HashIndex
from django.db import models


class AlmaMater(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Expertise(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Gender(models.Model):
    value = models.CharField(max_length=255, blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True,
    )

    class Meta:
        ordering = ('my_order',)

    def __str__(self):
        return self.value


class Language(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class HearFromUs(models.Model):
    value = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'HearFromUs'
        verbose_name_plural = 'HearFromUs'

    def __str__(self):
        return self.value


class Jurisdiction(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Date(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Practice(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Document(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Sector(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Department(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class AdoptedActor(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class LawyerCaseStatus(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Profession(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class EmploymentType(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Degree(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class LawyerSpecialization(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class LawyerSource(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class LawyerArea(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class Country(AbstractCountry):
    pass


connect_default_signals(Country)


class Region(AbstractRegion):
    pass


connect_default_signals(Region)


class City(AbstractCity):
    search_names = ToSearchTextField(max_length=4000, blank=True, default='')
    timezone = models.CharField(max_length=40)

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        indexes = (
            HashIndex(
                fields=('search_names',), name='%(app_label)s_%(class)s_search_names'
            ),
        )


connect_default_signals(City)


class SubRegion(AbstractSubRegion):
    pass


connect_default_signals(SubRegion)


def set_city_fields(sender, instance, items, **kwargs):
    instance.timezone = items[ICity.timezone]


cities_light.signals.city_items_post_import.connect(set_city_fields)


def file_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    hash_string = hashlib.md5(
        f'{instance.account.email}{instance.account.date_joined}{instance.account.id}'.encode()
    ).hexdigest()
    return f'files/{hash_string}/{filename}'


class FileUpload(models.Model):
    account = models.ForeignKey(
        'account.Account', related_name='file_upload_account', on_delete=models.CASCADE
    )
    file = models.FileField('File', upload_to=file_upload_path)

    @property
    def file_name(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.account.email


class Currency(models.Model):
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value
