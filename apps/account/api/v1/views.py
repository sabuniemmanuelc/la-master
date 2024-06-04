import copy
import re
from itertools import chain

from password_generator import PasswordGenerator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.cache import cache
from django.core.exceptions import ValidationError as djangoVe
from django.core.validators import validate_email
from django.db.models import Q, TextField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.account.api.v1.serializers import (
    AccountSerializer,
    ChangePasswordSerializer,
    LawyerAwardSerializer,
    LawyerCaseSerializer,
    LawyerEducationSerializer,
    LawyerExperienceSerializer,
    LawyerJurisdictionsSerializer,
    LawyerLicenseSerializer,
    LawyerPublicActivitySerializer,
    LawyerPublicationSerializer,
    LawyerRatingSerializer,
    LawyerServiceSerializer,
    ProfileSerializer,
    RegisterSerializer,
)
from apps.account.models import (
    Account,
    LawyerAward,
    LawyerCase,
    LawyerEducation,
    LawyerExperience,
    LawyerJurisdictions,
    LawyerLicense,
    LawyerPublicActivity,
    LawyerPublication,
    LawyerRating,
    LawyerService,
    Profile,
)
from apps.account.task import la_send_html_email
from apps.utils.authenticate import CsrfExemptSessionAuthentication
from apps.utils.models import SearchHistoryItems
from apps.utils.pagination import CursorPaginationWithOrdering, PaginationHandlerMixin
from la import settings


class AccountViewSet(APIView):
    """Вью для отображения пользователя."""

    def get_serializer(self, *args, **kwargs):
        return AccountSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Account.objects.all(), pk=self.request.user.pk)
        serializer = AccountSerializer(item)
        return Response(serializer.data)


class ProfileViewSet(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    from_search = False

    def get_object(self):
        account_id = self.request.user.pk
        request_query_params_id = self.request.query_params.get('id', None)
        if request_query_params_id:
            if request_query_params_id.isdigit():
                self.from_search = True
                account_id = request_query_params_id
        return get_object_or_404(Profile.objects.all(), account=account_id)

    def get_serializer_context(self):
        ret = {
            'search': self.from_search,
        }
        ret.update(super().get_serializer_context())
        return ret


class RegisterView(CreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (AllowAny,)
    queryset = Account.objects.all()
    serializer_class = RegisterSerializer


class ChangePasswordView(UpdateAPIView):
    queryset = Account.objects.all()
    serializer_class = ChangePasswordSerializer


class ResetPasswordView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            validate_email(kwargs['email'])
        except djangoVe:
            raise ValidationError
        user = get_object_or_404(Account, email=kwargs['email'])
        password = PasswordGenerator().generate()
        la_send_html_email.delay(
            'account/templates/templated_email/new_password_generated.html',
            'A new password has been generated for you',
            {
                'profile_link': 'https://legaldata.ltd/profile',
                'username': user.email,
                'password': password,
            },
            settings.EMAIL_HOST_USER,
            kwargs['email'],
        )
        with open('/tmp/passwords.log', 'a+') as f:
            f.write(f"{kwargs['email']} {password}\r\n")
        user.set_password(password)
        user.save()
        return Response(status=status.HTTP_200_OK)


class LawyerCaseView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerCaseSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerCaseSerializer(
                LawyerCase.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_cases = LawyerCaseSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_cases.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                if 'status' in le_for_create:
                    le_for_create["status_id"] = le_for_create.pop("status")
                if 'jurisdiction' in le_for_create:
                    le_for_create["jurisdiction_id"] = le_for_create.pop("jurisdiction")
                if 'decision' in le_for_create:
                    le_for_create["decision_id"] = le_for_create.pop("decision")
                le_obj = LawyerCase.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                if 'status' in le_for_update_copy:
                    le_for_update_copy["status_id"] = le_for_update_copy.pop("status")
                if 'jurisdiction' in le_for_update_copy:
                    le_for_update_copy["jurisdiction_id"] = le_for_update_copy.pop(
                        "jurisdiction"
                    )
                if 'decision' in le_for_update_copy:
                    le_for_update_copy["decision_id"] = le_for_update_copy.pop(
                        "decision"
                    )
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerCase.objects.filter(id=le_for_update_id).update(
                    **le_for_update_copy
                )
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerCase.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerCaseSerializer(
                LawyerCase.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerServiceView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerServiceSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerServiceSerializer(
                LawyerService.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_cases = LawyerServiceSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_cases.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                le_obj = LawyerService.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)
                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerService.objects.filter(id=le_for_update_id).update(
                    **le_for_update_copy
                )
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerService.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerServiceSerializer(
                LawyerService.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerExperienceView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerExperienceSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerExperienceSerializer(
                LawyerExperience.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_experience = LawyerExperienceSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_experience.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                if 'country' in le_for_create:
                    le_for_create["country_id"] = le_for_create.pop("country")
                if 'city' in le_for_create:
                    le_for_create["city_id"] = le_for_create.pop("city")
                if 'employment_type' in le_for_create:
                    le_for_create["employment_type_id"] = le_for_create.pop(
                        "employment_type"
                    )
                le_obj = LawyerExperience.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                if 'country' in le_for_update_copy:
                    le_for_update_copy["country_id"] = le_for_update_copy.pop("country")
                if 'city' in le_for_update_copy:
                    le_for_update_copy["city_id"] = le_for_update_copy.pop("city")
                if 'employment_type' in le_for_update_copy:
                    le_for_update_copy["employment_type_id"] = le_for_update_copy.pop(
                        "employment_type"
                    )
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerExperience.objects.filter(
                    id=le_for_update_id
                ).update(**le_for_update_copy)
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerExperience.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerExperienceSerializer(
                LawyerExperience.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerEducationView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerEducationSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerEducationSerializer(
                LawyerEducation.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_education = LawyerEducationSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_education.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                if 'degree' in le_for_create:
                    le_for_create["degree_id"] = le_for_create.pop("degree")
                if 'country' in le_for_create:
                    le_for_create["country_id"] = le_for_create.pop("country")
                if 'city' in le_for_create:
                    le_for_create["city_id"] = le_for_create.pop("city")
                if 'diploma' in le_for_create:
                    le_for_create["diploma_id"] = le_for_create.pop("diploma")

                le_obj = LawyerEducation.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                if 'degree' in le_for_update_copy:
                    le_for_update_copy["degree_id"] = le_for_update_copy.pop("degree")
                if 'country' in le_for_update_copy:
                    le_for_update_copy["country_id"] = le_for_update_copy.pop("country")
                if 'city' in le_for_update_copy:
                    le_for_update_copy["city_id"] = le_for_update_copy.pop("city")
                if 'diploma' in le_for_update_copy:
                    le_for_update_copy["diploma_id"] = le_for_update_copy.pop("diploma")

                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerEducation.objects.filter(
                    id=le_for_update_id
                ).update(**le_for_update_copy)
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerEducation.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerEducationSerializer(
                LawyerEducation.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerAwardView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerAwardSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerAwardSerializer(
                LawyerAward.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_award = LawyerAwardSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_award.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                if 'award' in le_for_create:
                    le_for_create["award_id"] = le_for_create.pop("award")
                le_obj = LawyerAward.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                if 'award' in le_for_update_copy:
                    le_for_update_copy["award_id"] = le_for_update_copy.pop("award")
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerAward.objects.filter(id=le_for_update_id).update(
                    **le_for_update_copy
                )
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerAward.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerAwardSerializer(
                LawyerAward.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerPublicationView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerPublicationSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerPublicationSerializer(
                LawyerPublication.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_award = LawyerPublicationSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_award.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                le_obj = LawyerPublication.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerPublication.objects.filter(
                    id=le_for_update_id
                ).update(**le_for_update_copy)
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerPublication.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerPublicationSerializer(
                LawyerPublication.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerPublicActivityView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerPublicActivitySerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerPublicActivitySerializer(
                LawyerPublicActivity.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_award = LawyerPublicActivitySerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_award.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                if 'country' in le_for_create:
                    le_for_create["country_id"] = le_for_create.pop("country")
                if 'city' in le_for_create:
                    le_for_create["city_id"] = le_for_create.pop("city")
                le_obj = LawyerPublicActivity.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                if 'country' in le_for_update_copy:
                    le_for_update_copy["country_id"] = le_for_update_copy.pop("country")
                if 'city' in le_for_update_copy:
                    le_for_update_copy["city_id"] = le_for_update_copy.pop("city")
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerPublicActivity.objects.filter(
                    id=le_for_update_id
                ).update(**le_for_update_copy)
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerPublicActivity.objects.filter(
                account_id=self.request.user.pk
            ).exclude(id__in=exist_ids).delete()
        return Response(
            LawyerPublicActivitySerializer(
                LawyerPublicActivity.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerRatingView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerRatingSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerRatingSerializer(
                LawyerRating.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_award = LawyerRatingSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_award.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                if 'source' in le_for_create:
                    le_for_create["source_id"] = le_for_create.pop("source")
                if 'area' in le_for_create:
                    le_for_create["area_id"] = le_for_create.pop("area")
                le_obj = LawyerRating.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                if 'source' in le_for_update_copy:
                    le_for_update_copy["source_id"] = le_for_update_copy.pop("source")
                if 'area' in le_for_update_copy:
                    le_for_update_copy["area_id"] = le_for_update_copy.pop("area")
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerRating.objects.filter(id=le_for_update_id).update(
                    **le_for_update_copy
                )
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerRating.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerRatingSerializer(
                LawyerRating.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerLicenseView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerLicenseSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerLicenseSerializer(
                LawyerLicense.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_award = LawyerLicenseSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_award.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                if 'country' in le_for_create:
                    le_for_create["country_id"] = le_for_create.pop("country")
                if 'city' in le_for_create:
                    le_for_create["city_id"] = le_for_create.pop("city")
                if 'license_file' in le_for_create:
                    le_for_create["license_file_id"] = le_for_create.pop("license_file")
                le_obj = LawyerLicense.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                if 'country' in le_for_update_copy:
                    le_for_update_copy["country_id"] = le_for_update_copy.pop("country")
                if 'city' in le_for_update_copy:
                    le_for_update_copy["city_id"] = le_for_update_copy.pop("city")
                if 'license_file' in le_for_update_copy:
                    le_for_update_copy["license_file_id"] = le_for_update_copy.pop(
                        "license_file"
                    )
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerLicense.objects.filter(id=le_for_update_id).update(
                    **le_for_update_copy
                )
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerLicense.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerLicenseSerializer(
                LawyerLicense.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerJurisdictionsView(APIView):
    def get_serializer(self, *args, **kwargs):
        return LawyerJurisdictionsSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(
            LawyerJurisdictionsSerializer(
                LawyerJurisdictions.objects.filter(account_id=self.request.user.pk),
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request, *args, **kwargs):  # noqa: C901
        request_data = copy.deepcopy(request.data)
        for rd in request_data:
            rd['account'] = request.user.id
        lawyer_award = LawyerJurisdictionsSerializer(
            data=request_data, many=True, context={"request": request}
        )
        exist_ids = []
        if lawyer_award.is_valid(raise_exception=True):
            create_object = []
            update_object = []
            for le in request_data:
                try:
                    le['id']
                except KeyError:
                    create_object.append(le)
                else:
                    update_object.append(le)

            for le_for_create in create_object:
                if 'account' in le_for_create:
                    le_for_create["account_id"] = le_for_create.pop("account")
                le_obj = LawyerJurisdictions.objects.create(**le_for_create)
                exist_ids.append(le_obj.id)

            for le_for_update in update_object:
                le_for_update_copy = copy.deepcopy(le_for_update)

                if 'account' in le_for_update_copy:
                    le_for_update_copy["account_id"] = le_for_update_copy.pop("account")
                le_for_update_id = le_for_update_copy['id']
                le_for_update_copy.pop('id', None)
                rows_update = LawyerJurisdictions.objects.filter(
                    id=le_for_update_id
                ).update(**le_for_update_copy)
                if rows_update:
                    exist_ids.append(le_for_update_id)

            LawyerJurisdictions.objects.filter(account_id=self.request.user.pk).exclude(
                id__in=exist_ids
            ).delete()
        return Response(
            LawyerJurisdictionsSerializer(
                LawyerJurisdictions.objects.filter(id__in=exist_ids),
                many=True,
                context={"request": request},
            ).data
        )


class LawyerSearchView(APIView, PaginationHandlerMixin):
    serializer_class = ProfileSerializer
    pagination_class = CursorPaginationWithOrdering

    def qs_params_to_array(self, param):
        return [int(val) for val in param.split(',')]

    def get(self, request, *args, **kwargs):  # noqa: C901
        query_params = copy.deepcopy(request.query_params)
        search_string = ''
        search_vector = (
            SearchVector('country__name')
            + SearchVector('city__name')
            + SearchVector('practice__value')
            + SearchVector('specializations')
            + SearchVector(Cast('specializations', TextField()))
            + SearchVector('profession__value')
            + SearchVector('expertise__value')
            + SearchVector('languages')
            + SearchVector(Cast('languages_text', TextField()))
            + SearchVector('interests')
            + SearchVector(Cast('interests', TextField()))
            + SearchVector('expertise__value')
            + SearchVector('jurisdictions')
            + SearchVector(Cast('jurisdictions_text', TextField()))
        )
        try:
            if 'search' in query_params:
                query_params_search = query_params.pop('search')[0]
                if query_params_search:
                    bad_symbol = "!@#$%^&*()+:"
                    search_string = re.sub(rf'[{bad_symbol}]', '', query_params_search)
                    search_string = search_string.split(' ')
                    search_string = ' & '.join(
                        [val.replace(':*', '') + ':*' for val in search_string]
                    )
            # Если нет строки поиска и фильтров, то возвращаем всех.
            if all((not search_string, not query_params)):
                # return Response([])
                qs = Profile.objects.filter(
                    verified=True,
                    search_visibility=True,
                )
                page = self.paginate_queryset(qs)
                if page is not None:
                    serializer = self.serializer_class(
                        page,
                        many=True,
                        context={
                            "request": request,
                            "search": True,
                        },
                    )
                    SearchHistoryItems.objects.create(
                        account_id=request.user.id,
                        entity_name='lawyers',
                        search_parameters={'section': 'lawyers', 'search': ''},
                        created_at=timezone.now(),
                        items_found_count=len(qs),
                    )
                    return self.get_paginated_response(serializer.data)

                serializer = self.serializer_class(
                    qs,
                    many=True,
                    context={
                        "request": request,
                        "search": True,
                    },
                )
                SearchHistoryItems.objects.create(
                    account_id=request.user.id,
                    entity_name='lawyers',
                    search_parameters={'section': 'lawyers', 'search': ''},
                    created_at=timezone.now(),
                    items_found_count=len(qs),
                )
                return Response(serializer.data)
            # Если есть строка поиска и нет фильтров, то возвращаем всех, где присутствует строка поиска.
            elif all((search_string, not query_params)):
                profiles = (
                    Profile.objects.select_related()
                    .annotate(
                        search=search_vector,
                    )
                    .filter(
                        Q(search=SearchQuery(search_string, search_type='raw'))
                        | Q(search_vector=SearchQuery(search_string, search_type='raw'))
                        & Q(
                            verified=True,
                        )
                        & Q(search_visibility=True),
                    )
                )

                lawyer_educations_experience = Profile.objects.select_related().filter(
                    Q(
                        id__in=LawyerEducation.objects.select_related()
                        .annotate(
                            search=(
                                SearchVector('description')
                                + SearchVector('id_diploma')
                                + SearchVector('license_id')
                            )
                        )
                        .filter(
                            search=SearchQuery(search_string, search_type='raw'),
                        )
                        .values_list('account__profile_account__id', flat=True)
                    )
                    | Q(
                        id__in=LawyerExperience.objects.select_related()
                        .annotate(search=(SearchVector('company_name')))
                        .filter(
                            search=SearchQuery(search_string, search_type='raw'),
                        )
                        .values_list('account__profile_account__id', flat=True)
                    )
                    & Q(
                        verified=True,
                    )
                    & Q(search_visibility=True),
                )

                qs = list(
                    chain(
                        profiles,
                        lawyer_educations_experience,
                    )
                )
                page = self.paginate_queryset(qs)
                if page is not None:
                    serializer = self.serializer_class(
                        page,
                        many=True,
                        context={
                            "request": request,
                            "search": True,
                        },
                    )
                    SearchHistoryItems.objects.create(
                        account_id=request.user.id,
                        entity_name='lawyers',
                        search_parameters={
                            'section': 'lawyers',
                            'search': search_string,
                        },
                        created_at=timezone.now(),
                        items_found_count=len(qs),
                    )
                    return self.get_paginated_response(serializer.data)

                serializer = self.serializer_class(
                    qs,
                    many=True,
                    context={
                        "request": request,
                        "search": True,
                    },
                )
                SearchHistoryItems.objects.create(
                    account_id=request.user.id,
                    entity_name='lawyers',
                    search_parameters={'section': 'lawyers', 'search': search_string},
                    created_at=timezone.now(),
                    items_found_count=len(qs),
                )
                return Response(serializer.data)
            # Если нет строки поиска и есть фильтры, то возвращаем всех, где присутствует фильтры.
            elif all((not search_string, query_params)):
                qs_filter = {}
                if 'profession' in query_params:
                    qs_filter.update(
                        {
                            'profession__id__in': self.qs_params_to_array(
                                query_params['profession']
                            )
                        }
                    )
                if 'language' in query_params:
                    qs_filter.update(
                        {
                            'languages__contains': self.qs_params_to_array(
                                query_params['language']
                            )
                        }
                    )
                if 'city' in query_params:
                    qs_filter.update(
                        {'city__id__in': self.qs_params_to_array(query_params['city'])}
                    )
                if 'country' in query_params:
                    qs_filter.update(
                        {
                            'country__id__in': self.qs_params_to_array(
                                query_params['country']
                            )
                        }
                    )

                qs = Profile.objects.select_related().filter(
                    **qs_filter,
                    verified=True,
                    search_visibility=True,
                )
                page = self.paginate_queryset(qs)
                if page is not None:
                    serializer = self.serializer_class(
                        page,
                        many=True,
                        context={
                            "request": request,
                            "search": True,
                        },
                    )
                    SearchHistoryItems.objects.create(
                        account_id=request.user.id,
                        entity_name='lawyers',
                        search_parameters={'section': 'lawyers', 'search': ''},
                        created_at=timezone.now(),
                        items_found_count=len(qs),
                    )
                    return self.get_paginated_response(serializer.data)

                serializer = self.serializer_class(
                    qs,
                    many=True,
                    context={
                        "request": request,
                        "search": True,
                    },
                )
                SearchHistoryItems.objects.create(
                    account_id=request.user.id,
                    entity_name='lawyers',
                    search_parameters={'section': 'lawyers', 'search': ''},
                    created_at=timezone.now(),
                    items_found_count=len(qs),
                )
                return Response(serializer.data)
            # Если есть строка поиска и есть фильтры, то возвращаем всех,
            # где присутствует строка поиска и фильтры.
            else:
                vector_filter = (
                    SearchVector('interests')
                    + SearchVector('specializations')
                    + SearchVector('expertise__value')
                    + SearchVector('jurisdictions')
                    + SearchVector('practice__value')
                    + SearchVector('country__name')
                    + SearchVector(Cast('interests', TextField()))
                    + SearchVector(Cast('specializations', TextField()))
                    + SearchVector('expertise__value')
                    + SearchVector(Cast('jurisdictions_text', TextField()))
                )

                qs_filter = {}
                if 'profession' in query_params:
                    qs_filter.update(
                        {
                            'profession__id__in': self.qs_params_to_array(
                                query_params['profession']
                            )
                        }
                    )
                if 'language' in query_params:
                    qs_filter.update(
                        {
                            'languages__contains': self.qs_params_to_array(
                                query_params['language']
                            )
                        }
                    )
                if 'city' in query_params:
                    qs_filter.update(
                        {'city__id__in': self.qs_params_to_array(query_params['city'])}
                    )
                if 'country' in query_params:
                    qs_filter.update(
                        {
                            'country__id__in': self.qs_params_to_array(
                                query_params['country']
                            )
                        }
                    )

                profiles = (
                    Profile.objects.select_related()
                    .annotate(
                        search=vector_filter,
                    )
                    .filter(
                        Q(search=SearchQuery(search_string, search_type='raw'))
                        | Q(search_vector=SearchQuery(search_string, search_type='raw'))
                        & Q(
                            verified=True,
                        )
                        & Q(search_visibility=True),
                        **qs_filter,
                    )
                )

                lawyer_educations_experience = profiles.filter(
                    Q(
                        id__in=LawyerEducation.objects.select_related()
                        .annotate(
                            search=(
                                SearchVector('description')
                                + SearchVector('id_diploma')
                                + SearchVector('license_id')
                            )
                        )
                        .filter(
                            search=SearchQuery(search_string, search_type='raw'),
                        )
                        .values_list('account__profile_account__id', flat=True)
                    )
                    | Q(
                        id__in=LawyerExperience.objects.select_related()
                        .annotate(search=(SearchVector('company_name')))
                        .filter(
                            search=SearchQuery(search_string, search_type='raw'),
                        )
                        .values_list('account__profile_account__id', flat=True)
                    ),
                )

                qs = list(
                    chain(
                        profiles,
                        lawyer_educations_experience,
                    )
                )

                page = self.paginate_queryset(qs)
                if page is not None:
                    serializer = self.serializer_class(
                        page,
                        many=True,
                        context={
                            "request": request,
                            "search": True,
                        },
                    )
                    SearchHistoryItems.objects.create(
                        account_id=request.user.id,
                        entity_name='lawyers',
                        search_parameters={
                            'section': 'lawyers',
                            'search': search_string,
                        },
                        created_at=timezone.now(),
                        items_found_count=len(qs),
                    )
                    return self.get_paginated_response(serializer.data)

                serializer = self.serializer_class(
                    qs,
                    many=True,
                    context={
                        "request": request,
                        "search": True,
                    },
                )
                SearchHistoryItems.objects.create(
                    account_id=request.user.id,
                    entity_name='lawyers',
                    search_parameters={'section': 'lawyers', 'search': search_string},
                    created_at=timezone.now(),
                    items_found_count=len(qs),
                )
                return Response(serializer.data)
        except Exception:
            return Response([])


class CheckAuthViewSet(APIView):
    def get(self, request, *args, **kwargs):
        user_auth = cache.get(
            f'user_auth{request.user.email}',
        )
        if user_auth is None:
            user_auth = Account.objects.get(id=request.user.id).has_access
        return Response({'user_auth': user_auth})
