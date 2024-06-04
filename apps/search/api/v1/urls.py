from rest_framework.routers import DefaultRouter

from django.urls import path

from apps.search.api.v1.views import SearchView

app_name = 'v1'

router = DefaultRouter(trailing_slash=False)

urlpatterns = router.urls

urlpatterns += [
    path('string/<str:string>', SearchView.as_view(), name='search_string'),
]
