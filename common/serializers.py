import json
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta, date

from .models import Room, Enrollment, Speciality, Polyclinic, WorkTime, Diagnosis
from users.models import User


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = '__all__'


class DoctorDataSerializer(serializers.ModelSerializer):
    speciality = SpecialitySerializer()

    class Meta:
        model = User
        fields = (
        "first_name", 'last_name', 'username', 'phone_number', 'is_doctor', 'speciality', 'polyclinic', 'room', 'level')


class DoctorShortDataSerializer(serializers.ModelSerializer):
    speciality = serializers.CharField(source='speciality.title')

    class Meta:
        model = User
        fields = ("id", "first_name", 'last_name', 'phone_number', 'speciality', 'level')

    # def get_speciality(self, obj):
    #     return obj.speciality.title


class RoomSerializer(serializers.ModelSerializer):
    doctor = DoctorShortDataSerializer(many=True)

    class Meta:
        model = Room
        fields = ('title', 'number', 'floor', 'doctor')


class PolyclinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Polyclinic
        fields = '__all__'


class PolyclinicDetailSerializer(serializers.ModelSerializer):
    room = RoomSerializer(many=True)

    class Meta:
        model = Polyclinic
        fields = ('number', 'district', 'address', 'room')


class EnrollmentListSerializer(serializers.ModelSerializer):
    doctor_speciality = serializers.SerializerMethodField()
    patient_last_name = serializers.SerializerMethodField()
    polyclinic = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ('doctor_speciality', 'patient_last_name', 'start_etime', 'end_etime', 'polyclinic', 'room')

    def get_doctor_speciality(self, obj):
        return obj.doctor.speciality.title

    def get_patient_last_name(self, obj):
        return obj.patient.last_name

    def get_polyclinic(self, obj):
        return obj.patient.polyclinic.number

    def get_room(self, obj):
        return obj.doctor.room.number


class DoctorPatientDataSerializer(serializers.ModelSerializer):
    speciality = SpecialitySerializer()

    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'phone_number', 'is_doctor', 'speciality', 'polyclinic', 'room', 'level')


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    doctor = DoctorPatientDataSerializer()
    patient = DoctorPatientDataSerializer()

    class Meta:
        model = Enrollment
        fields = '__all__'


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['doctor', 'start_etime', ]

    def create(self, validated_data):
        start_etime = validated_data.get('start_etime')
        doctor_id = validated_data.get('doctor')

        doctor_obj = User.objects.get(id=doctor_id.id)
        during = doctor_obj.work_time.first().during
        enrollment = Enrollment.objects.filter(doctor_id=doctor_id, start_etime=start_etime)
        if enrollment:
            raise serializers.ValidationError('Bu paytda doctor qabuliga yozila olmaysiz')
        elif start_etime.hour < 9 and start_etime.hour != 13 and start_etime.hour > 17:
            raise serializers.ValidationError('Docotr ish vaqti emas')
        elif start_etime < datetime.now().astimezone():
            raise serializers.ValidationError('vaqtni belgilashda xatolik')
        elif start_etime.weekday() == 6:  # and start_etime.weekday() != 5:
            raise serializers.ValidationError('yakshanba ish kuni emas')
        end_etime = start_etime + timedelta(minutes=during)
        validated_data['end_etime'] = end_etime
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['start_etime', 'doctor', 'end_etime']

    def validate(self, attrs):
        data = super().validate(attrs)
        start_etime = data['start_etime']
        doctor_id = data['doctor']
        enrollment = Enrollment.objects.filter(doctor_id=doctor_id, start_etime=start_etime)
        if enrollment:
            raise serializers.ValidationError('Bu paytda doctor qabuliga yozila olmaysiz')
        elif start_etime.hour < 9 and start_etime.hour != 13 and start_etime.hour > 17:
            raise serializers.ValidationError('Docotr ish vaqti emas')
        elif start_etime < datetime.now().astimezone():
            raise serializers.ValidationError('vaqtni belgilashda xatolik')
        elif start_etime.weekday() == 6:  # and start_etime.weekday() != 6:
            raise serializers.ValidationError('yakshanba ish kuni emas')
        return data

    def update(self, instance, validated_data):
        start_etime = validated_data.get('start_etime')
        doctor_obj = instance.doctor
        enrollment = Enrollment.objects.filter(doctor=doctor_obj, start_etime=start_etime)
        if enrollment:
            raise serializers.ValidationError('Bu paytda doctor qabuliga yozila olmaysiz')
        instance.start_etime = validated_data.get('start_etime', instance.start_etime)
        instance.end_etime = validated_data.get('end_etime', instance.end_etime)
        instance.doctor = validated_data.get('doctor', instance.doctor)
        instance.save()
        return instance


class WorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = ('weekday', 'start_work_time', 'end_work_time')


class WorkTimeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = '__all__'
        extra_kwargs = {
            'etimes': {'required': False}
        }

    def create(self, validated_data):
        etimes = {}
        during = validated_data.get('during')
        start_work_time = validated_data.get('start_work_time')
        end_work_time = validated_data.get('end_work_time')
        diff_time = datetime.combine(datetime.today(), end_work_time) - datetime.combine(date.today(), start_work_time)
        n = int(diff_time.total_seconds() // (60 * during))
        for i in range(n):
            item = datetime.combine(date.today(), start_work_time) + timedelta(minutes=during * i)
            etimes[i] = item.strftime("%H:%M:%S")
        etimes = json.dumps(etimes)
        validated_data['etimes'] = etimes
        return super().create(validated_data)

    def update(self, instance, validated_data):
        etimes = {}
        during = validated_data.get('during')
        start_work_time = validated_data.get('start_work_time')
        end_work_time = validated_data.get('end_work_time')
        diff_time = datetime.combine(datetime.today(), end_work_time) - datetime.combine(date.today(), start_work_time)
        n = int(diff_time.total_seconds() // (60 * during))
        for i in range(n):
            item = datetime.combine(date.today(), start_work_time) + timedelta(minutes=during * i)
            etimes[i] = item.strftime("%H:%M:%S")
        etimes = json.dumps(etimes)
        validated_data['etimes'] = etimes
        return super().update(instance, validated_data)


class DiagnosisCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'


class DiagnosisListDetailSerializer(serializers.ModelSerializer):
    enrollment_date = serializers.SerializerMethodField()
    enrollment_doctor = serializers.SerializerMethodField()
    enrollment_patient = serializers.SerializerMethodField()

    class Meta:
        model = Diagnosis
        fields = ['id', "enrollment", 'enrollment_date', 'enrollment_doctor', 'enrollment_patient', 'text']

    def get_enrollment_date(self, obj):
        return obj.enrollment.start_etime

    def get_enrollment_doctor(self, obj):
        return obj.enrollment.doctor.last_name

    def get_enrollment_patient(self, obj):
        return obj.enrollment.patient.last_name
