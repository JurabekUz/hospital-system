from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import UserRegistrationSerializer, DoctorRegistrationSerializer, UserDetialSerializer, \
    DoctorDetialSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class DoctorRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = DoctorRegistrationSerializer


class UserDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)

        if user.is_doctor:
            serializer = DoctorDetialSerializer(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        serializer = UserDetialSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

