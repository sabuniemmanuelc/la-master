from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.data.models import (
    AdoptedActor,
    AlmaMater,
    City,
    Country,
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
    Region,
    Sector,
    SubRegion,
)


class AlmaMaterSerializer(ModelSerializer[AlmaMater]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = AlmaMater
        fields = '__all__'


class ExpertiseSerializer(ModelSerializer[Expertise]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Expertise
        fields = '__all__'


class GenderSerializer(ModelSerializer[Gender]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Gender
        fields = '__all__'


class LanguageSerializer(ModelSerializer[Language]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Language
        fields = '__all__'


class HearFromUsSerializer(ModelSerializer[HearFromUs]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = HearFromUs
        fields = '__all__'


class JurisdictionSerializer(ModelSerializer[Jurisdiction]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Jurisdiction
        fields = '__all__'


class DateSerializer(ModelSerializer[Date]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Date
        fields = '__all__'


class PracticeSerializer(ModelSerializer[Practice]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Practice
        fields = '__all__'


class DocumentsSerializer(ModelSerializer[Document]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Document
        fields = '__all__'


class SectorSerializer(ModelSerializer[Sector]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Sector
        fields = '__all__'


class DepartmentsSerializer(ModelSerializer[Department]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Department
        fields = '__all__'


class AdoptedActorSerializer(ModelSerializer[AdoptedActor]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = AdoptedActor
        fields = '__all__'


class LawyerCaseStatusSerializer(ModelSerializer[LawyerCaseStatus]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = LawyerCaseStatus
        fields = '__all__'


class ProfessionSerializer(ModelSerializer[Profession]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Profession
        fields = '__all__'


class EmploymentTypeSerializer(ModelSerializer[EmploymentType]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = EmploymentType
        fields = '__all__'


class DegreeSerializer(ModelSerializer[Degree]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Degree
        fields = '__all__'


class LawyerSpecializationSerializer(ModelSerializer[LawyerSpecialization]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = LawyerSpecialization
        fields = '__all__'


class LawyerSourceSerializer(ModelSerializer[LawyerSource]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = LawyerSource
        fields = '__all__'


class LawyerAreaSerializer(ModelSerializer[LawyerArea]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = LawyerArea
        fields = '__all__'


class CountrySerializer(ModelSerializer[Country]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.name,
        }

    class Meta:
        model = Country
        fields = '__all__'


class RegionSerializer(ModelSerializer[Region]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.name,
        }

    class Meta:
        model = Region
        exclude = ('slug', 'country')


class SubRegionSerializer(ModelSerializer[SubRegion]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.name,
        }

    class Meta:
        model = SubRegion
        exclude = ('slug', 'country', 'region')


class CitySerializer(ModelSerializer[City]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.name,
        }

    class Meta:
        model = City
        exclude = ('slug', 'country', 'region', 'subregion')


class FileUploadSerializer(ModelSerializer[FileUpload]):
    def to_representation(self, obj):
        request = self.context.get('request')
        # target = reverse("api-data:v1:files_download", kwargs={'file_id': hashids.encode(obj.id)})
        return {
            'value': obj.id,
            # 'label': request.build_absolute_uri(target),
            'label': request.build_absolute_uri(obj.file.url),
        }

    class Meta:
        model = FileUpload
        fields = '__all__'


class FileDownloadSerializer(serializers.Serializer):
    file_id = serializers.CharField(max_length=255)


class CurrencySerializer(ModelSerializer[LawyerSource]):
    def to_representation(self, obj):
        return {
            'value': obj.id,
            'label': obj.value,
        }

    class Meta:
        model = Currency
        fields = '__all__'
