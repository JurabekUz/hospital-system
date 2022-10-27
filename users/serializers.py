from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import User
from common.models import Polyclinic


class UserDetialSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', "first_name", 'last_name', 'username', 'email', 'district', 'address', 'phone_number',
                  'passport', 'polyclinic')


class DoctorDetialSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', "first_name", 'last_name', 'username', 'email', 'district', 'address', 'phone_number',
                  'passport', 'polyclinic', 'speciality', 'room', 'level')


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'username', 'password', 'email', 'district', 'address', 'phone_number',
                  'passport', 'polyclinic')
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},
            'district': {'required': True},
            'username': {'required': True}
        }

    def create(self, validated_data):
        try:
            polyclinic = Polyclinic.objects.get(district=validated_data['district'])
        except Exception as error:
            raise APIException(detail={
                "success": False,
                "error": str(error)
            })

        validated_data['password'] = make_password(validated_data['password'])
        validated_data['polyclinic'] = polyclinic
        return super().create(validated_data)


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
        "first_name", 'last_name', 'username', 'password', 'email', 'is_doctor', 'district', 'address', 'phone_number',
        'passport', 'speciality', 'polyclinic', 'room', 'level')
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_doctor': {'required': True},
            'polyclinic': {'required': True},
            'room': {'required': True},
            'speciality': {'required': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
