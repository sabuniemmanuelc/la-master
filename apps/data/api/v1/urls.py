from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from django.urls import path

from apps.data.api.v1.views import (
    AdoptedActorViewSet,
    AllDictView,
    AlmaMaterViewSet,
    CityRegionViewSet,
    CountryViewSet,
    CurrencyViewSet,
    DateViewSet,
    DegreeViewSet,
    DepartmentsViewSet,
    DocumentsViewSet,
    EmploymentTypeViewSet,
    ExpertiseViewSet,
    FileDownloadView,
    FileUploadView,
    GenderViewSet,
    HearFromUsViewSet,
    JurisdictionViewSet,
    LanguageViewSet,
    LawyerAreaViewSet,
    LawyerCaseStatusViewSet,
    LawyerSourceViewSet,
    LawyerSpecializationViewSet,
    PracticeViewSet,
    ProfessionViewSet,
    RegionViewSet,
    SectorViewSet,
    SubRegionViewSet,
)

app_name = 'v1'

router = DefaultRouter(trailing_slash=False)
router.register('countries', CountryViewSet)
router.register('alma-mater', AlmaMaterViewSet)
router.register('expertise', ExpertiseViewSet)
router.register('gender', GenderViewSet)
router.register('language', LanguageViewSet)
router.register('hear-from-us', HearFromUsViewSet)
router.register('jurisdiction', JurisdictionViewSet)
router.register('date', DateViewSet)
router.register('practice', PracticeViewSet)
router.register('documents', DocumentsViewSet)
router.register('sector', SectorViewSet)
router.register('departments', DepartmentsViewSet)
router.register('adopted-actor', AdoptedActorViewSet)
router.register('lawyer-case-status', LawyerCaseStatusViewSet)
router.register('profession', ProfessionViewSet)
router.register('employment-type', EmploymentTypeViewSet)
router.register('degree', DegreeViewSet)
router.register('lawyer-specialization', LawyerSpecializationViewSet)
router.register('lawyer-source', LawyerSourceViewSet)
router.register('lawyer-area', LawyerAreaViewSet)
router.register('currency', CurrencyViewSet)


region_router = NestedDefaultRouter(router, 'countries', lookup='countries')
region_router.register('regions', RegionViewSet, basename='regions')

subregion_router = NestedDefaultRouter(region_router, 'regions', lookup='regions')
subregion_router.register('subregions', SubRegionViewSet, basename='subregions')

city_router = NestedDefaultRouter(router, 'countries', lookup='countries')
city_router.register('cities', CityRegionViewSet, basename='cities')


urlpatterns = router.urls
urlpatterns += region_router.urls
urlpatterns += subregion_router.urls
urlpatterns += city_router.urls
urlpatterns += [
    path('all', AllDictView.as_view(), name='all-dict'),
    path('file', FileUploadView.as_view(), name='files'),
    path('download/<str:file_id>', FileDownloadView.as_view(), name='files_download'),
]
