from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginAPIView,
    LogoutAPIView,
    RegisterView,
    RequestPasswordResetEmail,
    PasswordTokenCheckAPI,
    SetNewPasswordAPIView,
    EditUserAPIView,
    UsersListAPIView,
    VerifyEmail
)

# this helps in hiding Django's API View in Production
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("email-verify/", VerifyEmail.as_view(), name="email-verify"),
    path(
        "request-reset-password/",
        RequestPasswordResetEmail.as_view(),
        name="request-reset-password",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete",
        SetNewPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    path("edit-user/<int:id>", EditUserAPIView.as_view()),
    path("user-details/", UsersListAPIView.as_view(), name="user-details"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "utils.views.error_404"
handler500 = "utils.views.error_500"
# handler400 = 'rest_framework.exceptions.bad_request'
# handler500 = 'rest_framework.exceptions.server_error'
