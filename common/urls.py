from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import WorkTimeViewSet, PolyclinicListCreateAPIView, PolyclinicDetailAPIView, PolyclinicUpdateAPIView,\
    PolyclinicDestroyAPIView, DoctorWorkDaysListAPIView, DoctorFreeTimeListAPIView,\
    EnrollmentListCreateAPIView, EnrollmentUpdateDetailAPIView, DiagnosisViewSet

router = DefaultRouter()
router.register('work-time', WorkTimeViewSet, 'work-time')
router.register('diagnosis', DiagnosisViewSet, 'diagnosis')

urlpatterns = [
    path('', include(router.urls)),
    # Polyclinics
    path('polyclinic-list-create/', PolyclinicListCreateAPIView.as_view(),name = 'polyclinic_list_create'),
    path('polyclinic-detail/<int:pk>/', PolyclinicDetailAPIView.as_view(),name = 'polyclinic_detail'),
    path('polyclinic-update/<int:pk>/', PolyclinicUpdateAPIView.as_view(),name = 'polyclinic_update'),
    path('polyclinic-delete/<int:pk>/', PolyclinicDestroyAPIView.as_view(),name = 'polyclinic_delete'),

    path('doctor-work-days/<int:pk>/', DoctorWorkDaysListAPIView.as_view(), name='doctor_work_days'),
    path('doctor-free-times/<int:pk>/', DoctorFreeTimeListAPIView.as_view(), name='doctor_free_times'),
    path('enrollment-list-create/', EnrollmentListCreateAPIView.as_view(), name='enrollment_list_crete'),
    path('enrollment-update-detail-del/<int:pk>/', EnrollmentUpdateDetailAPIView.as_view(), name='enrollment_update_detail_del'),

]