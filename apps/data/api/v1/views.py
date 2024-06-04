from rest_framework import mixins, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from apps.data.api.v1.serializers import (
    AdoptedActorSerializer,
    AlmaMaterSerializer,
    CitySerializer,
    CountrySerializer,
    CurrencySerializer,
    DateSerializer,
    DegreeSerializer,
    DepartmentsSerializer,
    DocumentsSerializer,
    EmploymentTypeSerializer,
    ExpertiseSerializer,
    FileDownloadSerializer,
    FileUploadSerializer,
    GenderSerializer,
    HearFromUsSerializer,
    JurisdictionSerializer,
    LanguageSerializer,
    LawyerAreaSerializer,
    LawyerCaseStatusSerializer,
    LawyerSourceSerializer,
    LawyerSpecializationSerializer,
    PracticeSerializer,
    ProfessionSerializer,
    RegionSerializer,
    SectorSerializer,
    SubRegionSerializer,
)
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
from apps.utils.pagination import CursorPaginationWithOrdering
from la.settings import hashids


class CountryViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Вью для отображения страны."""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = CursorPaginationWithOrdering

    def get_queryset(self):
        q = self.request.query_params.get('q')
        if 'short' in self.request.query_params.keys():
            self.queryset = self.queryset.filter(
                code2__in=['AU', 'CA', 'FR', 'DE', 'IN', 'IE', 'IT', 'NZ', 'GB', 'US'],
            ).order_by('name')
        if q:
            return self.queryset.filter(name__icontains=q).order_by('name')
        return self.queryset


class RegionViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Вью для отображения региона."""

    serializer_class = RegionSerializer
    pagination_class = CursorPaginationWithOrdering

    def get_queryset(self):
        return Region.objects.select_related().filter(
            country__pk=self.kwargs['countries_pk']
        )


class SubRegionViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Вью для отображения субрегиона."""

    serializer_class = SubRegionSerializer
    pagination_class = CursorPaginationWithOrdering

    def get_queryset(self):
        qs_filter = {}
        if self.kwargs.get('countries_pk'):
            qs_filter['country__pk'] = self.kwargs.get('countries_pk')
        elif self.kwargs.get('regions_pk'):
            qs_filter['region__pk'] = self.kwargs.get('regions_pk')
        return SubRegion.objects.select_related().filter(**qs_filter)


class CityRegionViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Вью для отображения города."""

    serializer_class = CitySerializer
    pagination_class = CursorPaginationWithOrdering

    def get_queryset(self):
        qs_filter = {}
        select_filter = {  # noqa: F841
            'AU': [
                'Adelaide',
                'Brisbane',
                'Canberra',
                'Darwin',
                'Gold Coast',
                'Hobart',
                'Melbourne',
                'Perth',
                'Sydney',
                'Wollongong',
            ],
            'CA': [
                'Calgary',
                'Edmonton',
                'Hamilton',
                'Kingston',
                'Montréal',
                'Ottawa',
                'Québec',
                'Toronto',
                'Vancouver',
                'Winnipeg',
            ],
            'FR': [
                'Bordeaux',
                'Lille',
                'Lyon',
                'Marseille',
                'Montpellier',
                'Nantes',
                'Nice',
                'Paris',
                'Strasbourg',
                'Toulouse',
            ],
            'DE': [
                'Berlin',
                'Bremen',
                'Köln',
                'Düsseldorf',
                'Essen',
                'Frankfurt am Main',
                'Hamburg',
                'Leipzig',
                'Munich',
                'Stuttgart',
            ],
            'IN': [
                'Ahmedabad',
                'Bengaluru',
                'Chennai',
                'Delhi',
                'Hyderābād',
                'Kolkata',
                'Mumbai',
                'Pune',
                'Surat',
                'Visakhapatnam',
            ],
            'IE': [
                'Cork',
                'Drogheda',
                'Dublin',
                'Dundalk',
                'Gaillimh',
                'Luimneach',
                'Naas',
                'Sligo',
                'Swords',
                'Waterford',
            ],
            'IT': [
                'Bologna',
                'Catania',
                'Florence',
                'Genoa',
                'Milan',
                'Naples',
                'Palermo',
                'Rome',
                'Turin',
                'Venice',
            ],
            'NZ': [
                'Auckland',
                'Wellington',
                'Christchurch',
                'Hamilton',
                'Napier',
                'Tauranga',
                'Dunedin',
                'Palmerston North',
                'Nelson',
                'Rotorua',
            ],
            'GB': [
                'Belfast',
                'Birmingham',
                'Cardiff',
                'Edinburgh',
                'Glasgow',
                'Leeds',
                'Liverpool',
                'London',
                'Manchester',
                'Sheffield',
            ],
            'US': [
                'Boston',
                'Chicago',
                'Dallas',
                'Houston',
                'Los Angeles',
                'New York City',
                'Philadelphia',
                'San Francisco',
                'San Jose',
                'Washington, D.C.',
            ],
        }
        if self.kwargs.get('countries_pk'):
            # qs_filter['country__pk'] = self.kwargs.get('countries_pk')
            q = self.request.query_params.get('q')
            country = Country.objects.get(id=self.kwargs.get('countries_pk'))
            cities = City.objects.select_related().filter(country=country)
            try:
                if 'short' in self.request.query_params.keys():
                    cities = cities.filter(name__in=select_filter[country.code2])
            except KeyError:
                pass

            if q:
                return cities.filter(name__icontains=q)
            return cities.order_by('name')
        elif self.kwargs.get('regions_pk'):
            qs_filter['region__pk'] = self.kwargs.get('regions_pk')
        elif self.kwargs.get('city_pk'):
            qs_filter['subregion__pk'] = self.kwargs.get('subregions_pk')
        return City.objects.select_related().filter(**qs_filter)


class AlmaMaterViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """Вью для отображения альмаматер."""

    queryset = AlmaMater.objects.all()
    serializer_class = AlmaMaterSerializer


class ExpertiseViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """Вью для отображения экспертизы."""

    queryset = Expertise.objects.all()
    serializer_class = ExpertiseSerializer


class GenderViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """Вью для отображения гендера."""

    queryset = Gender.objects.all()
    serializer_class = GenderSerializer


class LanguageViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """Вью для отображения языка."""

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class HearFromUsViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """Вью для отображения информации от нас."""

    queryset = HearFromUs.objects.all()
    serializer_class = HearFromUsSerializer


class JurisdictionViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer


class DateViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Date.objects.all()
    serializer_class = DateSerializer


class PracticeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Practice.objects.all()
    serializer_class = PracticeSerializer


class DocumentsViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Document.objects.all()
    serializer_class = DocumentsSerializer


class SectorViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer


class DepartmentsViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Department.objects.all()
    serializer_class = DepartmentsSerializer


class AdoptedActorViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = AdoptedActor.objects.all()
    serializer_class = AdoptedActorSerializer


class LawyerCaseStatusViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = LawyerCaseStatus.objects.all()
    serializer_class = LawyerCaseStatusSerializer


class ProfessionViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class EmploymentTypeViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = EmploymentType.objects.all()
    serializer_class = EmploymentTypeSerializer


class DegreeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer


class LawyerSpecializationViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = LawyerSpecialization.objects.all()
    serializer_class = LawyerSpecializationSerializer


class LawyerSourceViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = LawyerSource.objects.all()
    serializer_class = LawyerSourceSerializer


class LawyerAreaViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = LawyerArea.objects.all()
    serializer_class = LawyerAreaSerializer


class CurrencyViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class AllDictView(APIView):
    def get(self, request, *args, **kwargs):
        expertise_serializer = ExpertiseSerializer(Expertise.objects.all(), many=True)
        gender_serializer = GenderSerializer(Gender.objects.all(), many=True)
        language_serializer = LanguageSerializer(Language.objects.all(), many=True)
        jurisdiction_serializer = JurisdictionSerializer(
            Jurisdiction.objects.all(), many=True
        )
        date_serializer = DateSerializer(Date.objects.all(), many=True)
        practice_serializer = PracticeSerializer(Practice.objects.all(), many=True)
        documents_serializer = DocumentsSerializer(Document.objects.all(), many=True)
        sector_serializer = SectorSerializer(Sector.objects.all(), many=True)
        departments_serializer = DepartmentsSerializer(
            Department.objects.all(), many=True
        )
        adopted_actor_serializer = AdoptedActorSerializer(
            AdoptedActor.objects.all(), many=True
        )
        lawyer_case_status_serializer = LawyerCaseStatusSerializer(
            LawyerCaseStatus.objects.all(), many=True
        )
        profession_serializer = ProfessionSerializer(
            Profession.objects.all(), many=True
        )
        employment_type_serializer = EmploymentTypeSerializer(
            EmploymentType.objects.all(), many=True
        )
        lawyer_specialization_serializer = LawyerSpecializationSerializer(
            LawyerSpecialization.objects.all(), many=True
        )
        lawyer_source_serializer = LawyerSourceSerializer(
            LawyerSource.objects.all(), many=True
        )
        lawyer_area_serializer = LawyerAreaSerializer(
            LawyerArea.objects.all(), many=True
        )
        degree_serializer = DegreeSerializer(Degree.objects.all(), many=True)
        file_upload_serializer = FileUploadSerializer(
            FileUpload.objects.filter(account=request.user),
            context={"request": request},
            many=True,
        )
        currency_serializer = CurrencySerializer(Currency.objects.all(), many=True)
        content = {
            'status': 1,
            'responseCode': status.HTTP_200_OK,
            'data': {
                'expertises': expertise_serializer.data,
                'genders': gender_serializer.data,
                'languages': language_serializer.data,
                'jurisdictions': jurisdiction_serializer.data,
                'dates': date_serializer.data,
                'practices': practice_serializer.data,
                'documents': documents_serializer.data,
                'sectors': sector_serializer.data,
                'departments': departments_serializer.data,
                'adopted_actors': adopted_actor_serializer.data,
                'lawyer_case_statuses': lawyer_case_status_serializer.data,
                'professions': profession_serializer.data,
                'employment_types': employment_type_serializer.data,
                'degrees': degree_serializer.data,
                'lawyer_specializations': lawyer_specialization_serializer.data,
                'lawyer_sources': lawyer_source_serializer.data,
                'lawyer_areas': lawyer_area_serializer.data,
                'currencies': currency_serializer.data,
                'files': file_upload_serializer.data,
            },
        }
        return Response(content)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer(self, *args, **kwargs):
        return FileUploadSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        item = FileUpload.objects.filter(account=self.request.user.pk)
        serializer = FileUploadSerializer(item, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        file_serializer = FileUploadSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(
                {'id': file_serializer.instance.id}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDownloadView(APIView):
    def get_serializer(self, *args, **kwargs):
        return FileDownloadSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        file_id = hashids.decode(kwargs['file_id'])
        response = HttpResponse()
        if any((not request.headers.get('X-Real-Ip'), not file_id)):
            response.status_code = 404
            response.content = 'The request should be come from Nginx server.'
            return response
        file = get_object_or_404(FileUpload, id=file_id[0], account=request.user.id)
        response["X-Accel-Redirect"] = file.file.url
        response['Content-Disposition'] = (
            'attachment; filename="' + file.file.name + '"'
        )
        del response['Content-Type']
        del response['Accept-Ranges']
        del response['Set-Cookie']
        del response['Cache-Control']
        del response['Expires']
        return response
