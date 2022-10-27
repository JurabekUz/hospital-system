
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import UserRegistrationAPIView, DoctorRegistrationAPIView, UserDetailAPIView

urlpatterns = [
    path('registration/', UserRegistrationAPIView.as_view()),
    path('registration-doctor/', DoctorRegistrationAPIView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/user-detail/', UserDetailAPIView.as_view()),
    # path('api/users/', include('users.urls')),
    path('api/', include('common.urls'))
]
