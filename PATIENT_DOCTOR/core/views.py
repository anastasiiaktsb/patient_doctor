import django_filters
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from PATIENT_DOCTOR.permissions import IsPatient, IsDoctor
from .serializers import AppointmentSerializer, DateRangeSerializer, PatientSerializer, DoctorSerializer
from .models import Appointment, Doctor, Patient


class AppointmentsListAPIView(ListAPIView):
    model = Appointment
    permission_classes = (IsAuthenticated, )
    serializer_class = AppointmentSerializer
    params_serializer = DateRangeSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'patient'):
            return user.patient.appointments.all()
        return user.doctor.appointments.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        if not hasattr(self.request.user, 'doctor'):
            return queryset
        serializer = self.params_serializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return self.model.find_in_date_range(serializer.data)


class AppointmentCancelAPIView(UpdateAPIView):
    permission_classes = [IsPatient]
    model = Appointment

    def get_queryset(self):
        return self.model.objects.filter(patient=self.request.user.patient)

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        appointment.reject()
        self.send_emails(appointment)
        return Response('Appointment was successfully canceled')

    @staticmethod
    def send_emails(appointment):
        emails = [appointment.doctor.user.email, appointment.patient.user.email]
        send_email_on_appointment_cancel.delay(appointment.appt_date, appointment.appt_time, emails)


class PatientFilter(django_filters.rest_framework.FilterSet):
    surname = django_filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Patient
        fields = ['surname', 'age', 'gender', 'number_of_teeth', 'number_of_surgeries', ]


class DoctorPatientsListAPIView(ListAPIView):
    permission_classes = (IsDoctor, )
    filter_backends = [django_filters.filters.OrderingFilter, DjangoFilterBackend, ]
    ordering_fields = ['surname', 'age', 'number_of_teeth', 'number_of_surgeries', ]
    filter_class = PatientFilter

    # def get_queryset(self):
    #     patient_ids = self.request.user.doctor.appointments.all().values_list('patient__id')
    #     return Patient.objects.filter(id__in=patient_ids)


class DoctorFilter(django_filters.rest_framework.FilterSet):
    surname = django_filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Doctor
        fields = ['surname', 'gender', ]


class PatientDoctorsListAPIView(ListAPIView):
    permission_classes = (IsPatient, )
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, ]
    ordering_fields = ['surname', ]
    filter_class = DoctorFilter
    #
    # def get_queryset(self):
    #     doctor_ids = self.request.user.patient.appointments.all().values_list('doctor__id')
    #     return Doctor.objects.filter(id__in=doctor_ids)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    def get_serializer_class(self):
        if hasattr(self.request.user, 'patient'):
            return PatientSerializer
        return DoctorSerializer

    def get_object(self):
        user = self.request.user
        if hasattr(user, 'patient'):
            return user.patient
        return user.doctor
