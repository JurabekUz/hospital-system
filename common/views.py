import datetime
import json
import io

from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, APIException
from rest_framework import permissions, status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView, ListAPIView
from rest_framework.views import APIView

from users.models import User
from .models import Polyclinic, Enrollment, WorkTime, Diagnosis
from .serializers import PolyclinicSerializer, PolyclinicDetailSerializer, EnrollmentListSerializer, \
    EnrollmentCreateSerializer, EnrollmentUpdateSerializer, EnrollmentDetailSerializer, \
    WorkTimeSerializer, DiagnosisListDetailSerializer, DiagnosisCreateUpdateDeleteSerializer, WorkTimeListSerializer
from .permissions import IsDoctor


class PolyclinicListCreateAPIView(ListCreateAPIView):
    queryset = Polyclinic.objects.all()
    serializer_class = PolyclinicSerializer
    permission_classes = [permissions.IsAdminUser]


class PolyclinicDetailAPIView(RetrieveAPIView):
    queryset = Polyclinic.objects.prefetch_related('room').all()
    serializer_class = PolyclinicDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class PolyclinicUpdateAPIView(UpdateAPIView):
    queryset = Polyclinic.objects.all()
    serializer_class = PolyclinicSerializer
    permission_classes = [permissions.IsAdminUser]


class PolyclinicDestroyAPIView(DestroyAPIView):
    queryset = Polyclinic.objects.all()
    serializer_class = PolyclinicSerializer
    permission_classes = [permissions.IsAdminUser]


class DoctorWorkDaysListAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):
        work_times = WorkTime.objects.filter(doctor_id=pk)  # .values('weekday', 'start_work_time', 'end_work_time')
        serialiser = WorkTimeSerializer(work_times, many=True)
        return Response(data=serialiser.data)


# docotor ning bosh vaqtlarini korish
class DoctorFreeTimeListAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):
        date = self.request.GET.get('date')
        print(date)
        if date:
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
            except Exception as error:
                raise APIException(detail={
                    "success": False,
                    "sabas": "vaqtfa ogirilmadi",
                    "error": str(error)
                })
        else:
            date = datetime.datetime.today()
        enrollments = Enrollment.objects.filter(
            doctor_id=pk,
            start_etime__date=date,
        )
        try:
            doctor_etimes = WorkTime.objects.filter(doctor_id=pk, weekday=date.weekday()).first().etimes
            freetimes = doctor_etimes.copy()

            for item in enrollments:
                for num, time_str in doctor_etimes.items():
                    freetime = datetime.datetime.strptime(time_str, '%H:%M:%S')
                    if item.start_etime.astimezone().time() == freetime.time():
                        del freetimes[num]
            # return Response(data=json.dumps({f"{date}": freetimes}), status=status.HTTP_200_OK)
            return Response(data=freetimes, status=status.HTTP_200_OK)
        except Exception as error:
            raise APIException(detail={
                "success": False,
                "sabab": "tekshiriahda xatolik",
                "error": str(error)
            })


class EnrollmentListCreateAPIView(ListCreateAPIView):
    queryset = Enrollment.objects.all().order_by('-id')
    serializer_class = EnrollmentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_doctor:
            date = self.request.GET.get('date')
            if date:
                date = datetime.datetime.strptime(date, '%Y-%m-%d').astimezone()
                print(date)
                print(date.tzname())
                queryset = Enrollment.objects.filter(doctor_id=self.request.user.id, start_etime__date=date)
            else:
                queryset = Enrollment.objects.filter(doctor_id=self.request.user.id,
                                                     start_etime__date=datetime.datetime.today())
            return queryset
        return Enrollment.objects.filter(patient_id=self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EnrollmentCreateSerializer
        return EnrollmentListSerializer


class EnrollmentUpdateDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        enrollment = Enrollment.objects.get(id=pk)
        if enrollment.patient != request.user:
            raise ValidationError("xatolik enrollment userga tegishli emas")

        buffer = io.BytesIO()
        x = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
        textob = x.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("Helvetica", 16)

        doctor = enrollment.doctor
        doctor_fullname = f"Doctor FIO: {doctor.get_full_name()}"
        speciality = doctor.speciality.title
        level = doctor.level
        room = doctor.room.number
        patient_fullname = request.user.get_full_name()

        start_etime = enrollment.start_etime.strftime("%m/%d/%Y, %H:%M:%S")
        end_etime = enrollment.end_etime.strftime("%m/%d/%Y, %H:%M:%S")
        textob.textLine(f"Doctor FIO: {doctor_fullname}")
        textob.textLine(speciality)
        textob.textLine(f"doctor level: {level}")
        textob.textLine(f"xona: {room}")
        textob.textLine(f"bemor: {patient_fullname}")
        textob.textLine(f"kirish vaqti: {start_etime}")
        textob.textLine(f"chiqish vaqti: {end_etime}")
        x.setTitle(f"made by jurabek developer:)")
        x.drawText(textob)
        x.showPage()
        x.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'{request.user.username}.pdf')

    def put(self, request, pk, *args, **kwargs):
        enrollment = Enrollment.objects.get(id=pk)

        data = self.request.data
        start_etime = data['start_etime']
        end_etime = data['end_etime']
        doctor_id = data['doctor']

        if enrollment.patient != request.user:
            raise ValidationError("xatolik enrollment userga tegishli emas")

        enrollment.doctor_id = doctor_id
        enrollment.start_etime = start_etime
        enrollment.end_etime = end_etime
        enrollment.save()

        enrollment.refresh_from_db()
        res_serializer = EnrollmentDetailSerializer(enrollment)
        return Response(data=res_serializer.data, status=status.HTTP_200_OK)


class WorkTimeViewSet(ModelViewSet):
    queryset = WorkTime.objects.all()
    serializer_class = WorkTimeListSerializer
    permission_classes = [permissions.IsAdminUser]


class DiagnosisViewSet(ModelViewSet):
    queryset = Diagnosis.objects.all().order_by('-id')
    serializer_class = DiagnosisListDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get_queryset(self):
        user = self.request.user
        patient = self.request.GET.get("patient")
        if patient:
            queryset = self.queryset.filter(enrollment__patient_id=patient)
        elif user.is_doctor:
            queryset = self.queryset.filter(enrollment__doctor_id=user.id)
            return queryset
        queryset = self.queryset.filter(enrollment__patient_id=user.id)
        return queryset
