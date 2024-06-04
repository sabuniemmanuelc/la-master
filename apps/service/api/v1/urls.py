from rest_framework.routers import DefaultRouter

from apps.service.api.v1.views import ServiceViewSet

app_name = 'v1'

router = DefaultRouter(trailing_slash=False)
router.register('', ServiceViewSet, basename='service')

urlpatterns = router.urls
