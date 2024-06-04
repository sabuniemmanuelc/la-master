from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.account.api.v1.views import (
    AccountViewSet,
    ChangePasswordView,
    CheckAuthViewSet,
    LawyerAwardView,
    LawyerCaseView,
    LawyerEducationView,
    LawyerExperienceView,
    LawyerJurisdictionsView,
    LawyerLicenseView,
    LawyerPublicActivityView,
    LawyerPublicationView,
    LawyerRatingView,
    LawyerSearchView,
    LawyerServiceView,
    ProfileViewSet,
    RegisterView,
    ResetPasswordView,
)

app_name = 'v1'

urlpatterns = [
    path('user', AccountViewSet.as_view(), name='user'),
    path('user/profile', ProfileViewSet.as_view(), name='profile'),
    path('login', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('register', csrf_exempt(RegisterView.as_view()), name='auth_register'),
    path(
        'change_password/<int:pk>',
        ChangePasswordView.as_view(),
        name='auth_change_password',
    ),
    path(
        'reset_password/<str:email>',
        csrf_exempt(ResetPasswordView.as_view()),
        name='auth_reset_password',
    ),
    path('search', LawyerSearchView.as_view(), name='account_search'),
    path('education', LawyerEducationView.as_view(), name='account_education'),
    path('experience', LawyerExperienceView.as_view(), name='account_experience'),
    path('cases', LawyerCaseView.as_view(), name='account_cases'),
    path('awards', LawyerAwardView.as_view(), name='account_awards'),
    path('publications', LawyerPublicationView.as_view(), name='account_publications'),
    path('activities', LawyerPublicActivityView.as_view(), name='account_activities'),
    path('ratings', LawyerRatingView.as_view(), name='account_ratings'),
    path('licenses', LawyerLicenseView.as_view(), name='account_licenses'),
    path(
        'jurisdictions', LawyerJurisdictionsView.as_view(), name='account_jurisdictions'
    ),
    path('services', LawyerServiceView.as_view(), name='account_services'),
    path('check-auth', CheckAuthViewSet.as_view(), name='account_check_auth'),
]
