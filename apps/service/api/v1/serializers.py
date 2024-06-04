from rest_framework.serializers import ModelSerializer

from apps.service.models import Service


class ServiceSerializer(ModelSerializer[Service]):
    """Сериализатор сервисов."""

    class Meta:
        ref_name = 'ServiceSerializer'
        model = Service
        fields = [
            'name',
            'cost',
            'describe',
            'date_created',
            'enabled',
            'amount_days',
        ]
