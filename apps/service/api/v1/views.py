from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.service.api.v1.serializers import ServiceSerializer
from apps.service.models import Service


class ServiceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """Вью для отображения сервисов."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
