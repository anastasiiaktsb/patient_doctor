from django.urls import path, include
from rest_framework import routers


from .views import (
    AppointmentCancelAPIView,
    DoctorPatientsListAPIView,
    PatientDoctorsListAPIView,
    AppointmentsListAPIView,
    UserRetrieveUpdateAPIView,
)

router = routers.DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('me/', UserRetrieveUpdateAPIView.as_view(), name='user-info'),

    path('appointments/<pk>/cancel/', AppointmentCancelAPIView.as_view(), name='cancel-appointment'),

    path('patients/', DoctorPatientsListAPIView.as_view(), name='doctor-patients'),

    path('doctors/', PatientDoctorsListAPIView.as_view(), name='patient-doctors'),

    path('appointments/', AppointmentsListAPIView.as_view(), name='appointments'),
]

