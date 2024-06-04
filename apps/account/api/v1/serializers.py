import copy
from datetime import timedelta

from password_generator import PasswordGenerator
from phonenumber_field.phonenumber import to_python
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumbers import PhoneNumber
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as djangoVe
from django.core.validators import validate_email

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
from apps.account.task import la_send_html_email, send_meta_pixel_event
from apps.billing.models import Invoice
from apps.data.api.v1.serializers import (
    CitySerializer,
    CountrySerializer,
    DegreeSerializer,
    EmploymentTypeSerializer,
    FileUploadSerializer,
    GenderSerializer,
    LawyerCaseStatusSerializer,
    PracticeSerializer,
    ProfessionSerializer,
)
from apps.data.models import Country, Expertise, FileUpload, Language
from apps.service.models import Service
from apps.utils.get_client_ip import get_client_ip
from la import settings
from la.settings import TRIAL_PERIOD_DAYS


class AccountSerializer(ModelSerializer[Account]):
    """Сериализатор пользователя."""

    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise ValidationError()
        return value

    class Meta:
        ref_name = 'AccountSerializer'
        model = Account
        fields = [
            'id',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=Account.objects.all(),
                message='This email is already registered',
            )
        ],
    )

    class Meta:
        model = Account
        fields = ('email',)

    def validate(self, attrs):
        if not attrs['email']:
            raise serializers.ValidationError({"email": ["Email field empty."]})
        return attrs

    def create(self, validated_data):
        try:
            validate_email(validated_data['email'])
        except djangoVe:
            raise ValidationError
        if Account.objects.filter(
            email__iexact=str(validated_data['email']).lower()
        ).exists():
            raise serializers.ValidationError(
                {"email": ["This email is already registered"]}
            )
        user = Account.objects.create(email=str(validated_data['email']).lower())
        Profile.objects.create(account=user)
        password = PasswordGenerator().generate()
        la_send_html_email.delay(
            'account/templates/templated_email/welcome_email.html',
            'Welcome to Legal Data!',
            {
                'profile_link': 'https://legaldata.ltd/profile',
                'username': user.email,
                'password': password,
            },
            settings.EMAIL_HOST_USER,
            validated_data['email'],
        )
        send_meta_pixel_event.delay(
            client_email=validated_data['email'],
            client_ip=get_client_ip(self.context['request']),
        )
        # la_send_email.delay("Welcome to LegalData.", f"You password is {password}",
        #                     settings.EMAIL_HOST_USER, validated_data['email'])
        with open('/tmp/passwords.log', 'a+') as f:
            f.write(f"{validated_data['email']} {password}\r\n")
        user.set_password(password)
        user.save()
        if settings.INVOICE_ENABLED:
            Invoice.objects.create(
                account=user,
                service=Service.objects.get(id=1),
                due_date=user.date_joined + timedelta(days=TRIAL_PERIOD_DAYS),
            )
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ('password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs


class CustomPhoneNumberField(PhoneNumberField):
    """Класс для парсинга телефонных номеров."""

    def to_internal_value(self, phone: str) -> PhoneNumber:
        phone_number = to_python(phone)
        # if phone_number and not phone_number.is_valid():
        #     raise ValidationError(self.error_messages['invalid'])
        return phone_number


class LawyerCaseSerializer(ModelSerializer[LawyerCase]):
    id = serializers.IntegerField(required=False)

    def to_representation(self, obj):
        request = self.context.get('request')
        resp = super().to_representation(obj)
        resp = copy.deepcopy(resp)
        if resp['decision']:
            decision = FileUpload.objects.get(id=resp['decision'])
            # target = reverse("api-data:v1:files_download", kwargs={'file_id': hashids.encode(decision.id)})
            resp['decision'] = {
                'value': decision.id,
                # 'label': request.build_absolute_uri(target),
                'label': request.build_absolute_uri(decision.file.url),
            }
        if resp['jurisdiction']:
            resp['jurisdiction'] = LawyerJurisdictionsSerializer(obj.jurisdiction).data
        if resp['status']:
            resp['status'] = LawyerCaseStatusSerializer(obj.status).data
        return resp

    class Meta:
        model = LawyerCase
        fields = '__all__'


class LawyerServiceSerializer(ModelSerializer[LawyerService]):
    id = serializers.IntegerField(required=False)

    def to_representation(self, obj):
        resp = super().to_representation(obj)
        resp = copy.deepcopy(resp)
        if resp['account']:
            resp['account'] = AccountSerializer(obj.account).data
        return resp

    class Meta:
        model = LawyerService
        fields = '__all__'


class LawyerExperienceSerializer(ModelSerializer[LawyerExperience]):
    id = serializers.IntegerField(required=False)

    def to_representation(self, obj):
        resp = super().to_representation(obj)
        resp = copy.deepcopy(resp)
        if resp['account']:
            resp['account'] = AccountSerializer(obj.account).data
        if resp['country']:
            resp['country'] = CountrySerializer(obj.country).data
        if resp['city']:
            resp['city'] = CitySerializer(obj.city).data
        if resp['employment_type']:
            resp['employment_type'] = EmploymentTypeSerializer(obj.employment_type).data
        return resp

    class Meta:
        model = LawyerExperience
        fields = '__all__'


class LawyerEducationSerializer(ModelSerializer[LawyerEducation]):
    id = serializers.IntegerField(required=False)

    def to_representation(self, obj):
        request = self.context.get('request')
        resp = super().to_representation(obj)
        resp = copy.deepcopy(resp)
        if resp['account']:
            resp['account'] = AccountSerializer(obj.account).data
        if resp['country']:
            resp['country'] = CountrySerializer(obj.country).data
        if resp['city']:
            resp['city'] = CitySerializer(obj.city).data
        if resp['degree']:
            resp['degree'] = DegreeSerializer(obj.degree).data
        if all((resp['diploma'], not self.context.get('search', False))):
            resp['diploma'] = FileUploadSerializer(
                obj.diploma, context={"request": request}
            ).data
        else:
            resp['diploma'] = None
        if all((resp['id_diploma'], self.context.get('search', False))):
            resp['id_diploma'] = ''
        if all((resp['license_id'], self.context.get('search', False))):
            resp['license_id'] = ''
        return resp

    class Meta:
        model = LawyerEducation
        fields = '__all__'


class LawyerAwardSerializer(ModelSerializer[LawyerAward]):
    id = serializers.IntegerField(required=False)

    def to_representation(self, obj):
        request = self.context.get('request')
        resp = super().to_representation(obj)
        resp = copy.deepcopy(resp)
        if resp['award']:
            award = FileUpload.objects.get(id=resp['award'])
            # target = reverse("api-data:v1:files_download", kwargs={'file_id': hashids.encode(award.id)})
            resp['award'] = {
                'value': award.id,
                # 'label': request.build_absolute_uri(target),
                'label': request.build_absolute_uri(award.file.url),
            }
        return resp

    class Meta:
        model = LawyerAward
        fields = '__all__'


class LawyerPublicationSerializer(ModelSerializer[LawyerPublication]):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = LawyerPublication
        fields = '__all__'


class LawyerPublicActivitySerializer(ModelSerializer[LawyerPublicActivity]):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = LawyerPublicActivity
        fields = '__all__'


class LawyerRatingSerializer(ModelSerializer[LawyerRating]):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = LawyerRating
        fields = '__all__'


class LawyerLicenseSerializer(ModelSerializer[LawyerLicense]):
    id = serializers.IntegerField(required=False)

    def to_representation(self, obj):
        request = self.context.get('request')
        resp = super().to_representation(obj)
        resp = copy.deepcopy(resp)
        if resp['license_file']:
            license_file = FileUpload.objects.get(id=resp['license_file'])
            # target = reverse("api-data:v1:files_download", kwargs={'file_id': hashids.encode(license_file.id)})
            resp['license_file'] = {
                'value': license_file.id,
                # 'label': request.build_absolute_uri(target),
                'label': request.build_absolute_uri(license_file.file.url),
            }
        return resp

    class Meta:
        model = LawyerLicense
        fields = '__all__'


class LawyerJurisdictionsSerializer(ModelSerializer[LawyerJurisdictions]):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = LawyerJurisdictions
        fields = '__all__'


class ProfileSerializer(ModelSerializer[Profile]):
    """Сериализатор профиля пользователя."""

    account_email = serializers.EmailField(source='account.email')
    cases = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    educations = serializers.SerializerMethodField()
    awards = serializers.SerializerMethodField()
    publications = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    licenses = serializers.SerializerMethodField()

    def get_cases(self, profile):
        return LawyerCaseSerializer(
            profile.account.lawyer_case_account.all(), many=True
        ).data

    def get_services(self, profile):
        return LawyerServiceSerializer(
            profile.account.lawyer_service_account.all(), many=True
        ).data

    def get_experiences(self, profile):
        return LawyerExperienceSerializer(
            profile.account.lawyer_experience_account.all(), many=True
        ).data

    def get_educations(self, profile):
        return LawyerEducationSerializer(
            profile.account.lawyer_education_account.all(),
            many=True,
            context={
                "request": self.context['request'],
                "search": self.context.get('search', None),
            },
        ).data

    def get_awards(self, profile):
        return LawyerAwardSerializer(
            profile.account.lawyer_award_account.all(), many=True
        ).data

    def get_publications(self, profile):
        return LawyerPublicationSerializer(
            profile.account.lawyer_publication_account.all(), many=True
        ).data

    def get_activities(self, profile):
        return LawyerPublicActivitySerializer(
            profile.account.lawyer_public_activity_account.all(), many=True
        ).data

    def get_ratings(self, profile):
        return LawyerRatingSerializer(
            profile.account.lawyer_rating_account.all(), many=True
        ).data

    def get_licenses(self, profile):
        return LawyerLicenseSerializer(
            profile.account.lawyer_license_account.all(), many=True
        ).data

    def update(self, instance, validated_data):
        account = validated_data.pop('account', None)
        instance = super().update(instance, validated_data)
        if account:
            instance.account.email = account['email']
        if all((validated_data.get('country', None), validated_data.get('city', None))):
            if validated_data['city'].country != validated_data['country']:
                instance.city = None
        instance.account.save()
        return instance

    def create(self, validated_data):
        pass

    def to_representation(self, obj):  # noqa: C901
        request = self.context.get('request')
        # iterable = obj.all() if isinstance(obj, models.Manager) else [obj]
        # for it in iterable:
        resp = super().to_representation(obj)
        resp = copy.deepcopy(resp)
        if obj.account:
            resp['account'] = AccountSerializer(obj.account).data
        if obj.country:
            resp['country'] = CountrySerializer(
                obj.country,
                # source=Country.objects.filter(code2__in=['AU', 'CA', 'FR', 'DE', 'IN', 'IE', 'IT', 'NZ', 'GB', 'US']),
            ).data
        if obj.city:
            resp['city'] = CitySerializer(obj.city).data
        if obj.gender:
            resp['gender'] = GenderSerializer(obj.gender).data
        if obj.profession:
            resp['profession'] = ProfessionSerializer(obj.profession).data
        if obj.practice:
            resp['practice'] = PracticeSerializer(obj.practice).data
        if obj.jurisdictions:
            resp['jurisdictions'] = []
            jurisdictions = Country.objects.filter(id__in=obj.jurisdictions)
            for jurisdiction in jurisdictions:
                resp['jurisdictions'].append(
                    {
                        'value': jurisdiction.id,
                        'label': jurisdiction.name,
                    }
                )
        if obj.languages:
            resp['languages'] = []
            languages = Language.objects.filter(id__in=obj.languages)
            for language in languages:
                resp['languages'].append(
                    {
                        'value': language.id,
                        'label': language.value,
                    }
                )
        if obj.expertise:
            resp['expertise'] = []
            expertises = Expertise.objects.filter(
                id__in=obj.expertise.values_list('id', flat=True)
            )
            for expertise in expertises:
                resp['expertise'].append(
                    {
                        'value': expertise.id,
                        'label': expertise.value,
                    }
                )
        if obj.avatar:
            resp['avatar'] = FileUploadSerializer(
                obj.avatar, context={"request": request}
            ).data
        if obj.mobile_phone_number:
            if self.context.get('search', True):
                resp['mobile_phone_number'] = (
                    obj.mobile_phone_number if obj.phone_visibility else ''
                )
            else:
                resp['mobile_phone_number'] = obj.mobile_phone_number
        return resp

    class Meta:
        ref_name = 'AccountProfileSerializer'
        model = Profile
        fields = [
            # 'id',
            'account',
            'avatar',
            'languages',
            'country',
            'city',
            'birthday',
            'gender',
            'cases',
            'specializations',
            'interests',
            'real_name',
            'description',
            'verified',
            'rate',
            'experience_description',
            'search_visibility',
            'phone_visibility',
            'online_visibility',
            'profession',
            'services',
            'experiences',
            'educations',
            'awards',
            'publications',
            'activities',
            'ratings',
            'licenses',
            'jurisdictions',
            'practice',
            'mobile_phone_number',
            'email',
            'address',
            'work_phone_number',
            'website',
            'instagram',
            'facebook',
            'linkedin',
            'telegram',
            'whatsapp',
            'twitter',
            'account_email',
            'sending_notifications',
            'sending_browser_notifications',
        ]
