from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.contrib import admin
from django.urls import include, path, re_path

schema_view = get_schema_view(
    openapi.Info(
        title="LegalData API",
        default_version='v1',
        description="MVP project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=[permissions.IsAuthenticated],
)

urlpatterns_swagger = [
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json',
    ),
    re_path(
        r'^swagger$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    re_path(
        r'^redoc$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'
    ),
]

urlpatterns = [
    path('admin', admin.site.urls),
    path(
        'api/account/',
        include(
            'apps.account.api.urls',
            namespace='api-accounts',
        ),
    ),
    path(
        'api/service/',
        include(
            'apps.service.api.urls',
            namespace='api-services',
        ),
    ),
    path(
        'api/support/',
        include(
            'apps.support.api.urls',
            namespace='api-support',
        ),
    ),
    path(
        'api/data/',
        include(
            'apps.data.api.urls',
            namespace='api-data',
        ),
    ),
    path(
        'api/notification/',
        include(
            'apps.notification.api.urls',
            namespace='api-notification',
        ),
    ),
    path(
        'api/find/',
        include(
            'apps.search.api.urls',
            namespace='api-search',
        ),
    ),
    path(
        'api/favorites/',
        include(
            'apps.favorites.api.urls',
            namespace='api-favorites',
        ),
    ),
    path(
        'api/billing/',
        include(
            'apps.billing.api.urls',
            namespace='api-billing',
        ),
    ),
    path('tinymce/', include('tinymce.urls')),
    # path('__debug__/', include('debug_toolbar.urls')),
] + urlpatterns_swagger
