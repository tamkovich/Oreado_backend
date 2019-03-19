from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

from auth_page.api.views import AuthAPI


app_name = "auth-api"

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("credentials/", AuthAPI.as_view(), name="credentials"),
]
