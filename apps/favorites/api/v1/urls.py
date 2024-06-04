from rest_framework.routers import DefaultRouter

from apps.favorites.api.v1.views import FavoritesViewset

app_name = 'v1'

router = DefaultRouter(trailing_slash=False)
router.register('favorites', FavoritesViewset)

urlpatterns = router.urls
