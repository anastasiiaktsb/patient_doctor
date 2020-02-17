import datetime

from django.utils import timezone, dates
from rest_framework import serializers

from .models import Appointment, Doctor, Patient
from .tasks import send_email_on_appointment_reschedule

DINNER_TIME = 13


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'id', 'status', 'appt_date', 'appt_time',
        )
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        for attr in ['doctor', 'patient', 'status']:
            validated_data.pop(attr, None)

        instance = super().update(instance, validated_data)
        if self._is_datetime_modified(validated_data):
            emails = [instance.doctor.user.email, instance.patient.user.email]
            send_email_on_appointment_reschedule.delay(instance.appt_date, instance.appt_time, emails)
        return instance

    def validate(self, attrs):
        self._check_for_datetime_exceptions(attrs)
        if not self.instance or (self.instance and self._is_datetime_modified(attrs)):
            self._check_for_reserved_appointment(attrs)
        return attrs

    def _is_datetime_modified(self, attrs):
        if not self.instance:
            return
        for attr in ['appt_time', 'appt_date']:
            if getattr(self.instance, attr) != attrs.get(attr):
                return True

    @staticmethod
    def _check_for_reserved_appointment(attrs):
        appointment = Appointment.objects.filter(
            doctor=attrs.get('doctor'), appt_date=attrs.get('appt_date'),
            appt_time=attrs.get('appt_time'), status=Appointment.PENDING
        )
        if appointment.exists():
            raise serializers.ValidationError("This date is reserved.")

    @staticmethod
    def _check_for_datetime_exceptions(attrs):
        appt_time = attrs.get('appt_time')
        provided_datetime = attrs.get('appt_date').replace(hours=appt_time)
        if provided_datetime <= timezone.now():
            raise serializers.ValidationError("You provided past datetime.")

        if provided_datetime.hour == DINNER_TIME:
            raise serializers.ValidationError("We are eating!")

        if not (datetime.time(hour=9) <= appt_time < datetime.time(hour=18)):
            raise serializers.ValidationError("We are resting!")

        weekday = dates.WEEKDAYS[provided_datetime.weekday()]
        if weekday in ['Saturday', 'Sunday']:
            raise serializers.ValidationError("We are fucking our wives!")


class DateRangeSerializer(serializers.Serializer):
    since = serializers.DateField()
    until = serializers.DateField()

class DoctorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True)
    password = serializers.CharField(source='user.password', write_only=True)

    class Meta:
        model = Doctor
        fields = ('id', 'username', 'email', 'password', 'surname', 'gender',)
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        user_info = validated_data.pop('user', {})
        email = user_info.get('email')
        validated_data.pop('password', None)
        user = instance.user
        if email and email != user.email:
            user.email = emaildjango_content_type
            user.save()
        instance = super().update(instance, validated_data)
        return instance

class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True)
    password = serializers.CharField(source='user.password', write_only=True)

    class Meta:
        model = Patient
        fields = ('id', 'username', 'email', 'password', 'surname', 'gender', 'age', 'number_of_teeth',
                  'number_of_surgeries',)
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        user_info = validated_data.pop('user', {})
        email = user_info.get('email')
        validated_data.pop('password', None)
        user = instance.user
        if email and email != user.email:
            user.email = email
            user.save()
        instance = super().update(instance, validated_data)
        return instance
