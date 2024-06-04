from adminsortable2.admin import SortableAdminMixin

from django.contrib import admin

from apps.data.models import (
    AdoptedActor,
    AlmaMater,
    Currency,
    Date,
    Degree,
    Department,
    Document,
    EmploymentType,
    Expertise,
    FileUpload,
    Gender,
    HearFromUs,
    Jurisdiction,
    Language,
    LawyerArea,
    LawyerCaseStatus,
    LawyerSource,
    LawyerSpecialization,
    Practice,
    Profession,
    Sector,
)


@admin.register(AlmaMater)
class AlmaMaterAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Gender)
class GenderAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(HearFromUs)
class HearFromUsAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Jurisdiction)
class JurisdictionAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Date)
class DateAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(AdoptedActor)
class AdoptedActorAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(LawyerCaseStatus)
class LawyerCaseStatusAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(EmploymentType)
class EmploymentTypeAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(LawyerSpecialization)
class LawyerSpecializationAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(LawyerSource)
class LawyerSourceAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(LawyerArea)
class LawyerAreaAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
    search_fields = ('value',)


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('account', 'file')
    list_filter = ('account', 'file')
    search_fields = ('account__email',)
    list_select_related = ('account',)
    raw_id_fields = ('account',)
