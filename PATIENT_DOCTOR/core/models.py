from django.contrib.auth.models import models
from django.core.validators import MinValueValidator, MaxValueValidator

from PATIENT_DOCTOR.authentication.models import BaseProfile


class FindInDateRangeMixin:

    @classmethod
    def _find_in_date_range(cls, field, since=None, until=None):
        filter_params = {}
        field_name = field.field_name
        if since:
            filter_params[f'{field_name}__gte'] = since
        if until:
            filter_params[f'{field_name}__lte'] = until
        return cls.objects.filter(**filter_params)


class Appointment(
    FindInDateRangeMixin,
    models.Model,
):
    PENDING = 1
    REJECTED = 2
    FINISHED = 3
    ORDER_STATUS = (
        (PENDING, "Pending"),
        (REJECTED, "Rejected"),
        (FINISHED, "Finished")
    )
    status = models.PositiveSmallIntegerField(choices=ORDER_STATUS, default=PENDING)
    appt_datetime = models.DateTimeField()
    doctor = models.ForeignKey(related_name='appointments', on_delete=models.CASCADE, to='core.Doctor')
    patient = models.ForeignKey(related_name='appointments', on_delete=models.CASCADE, to='core.Patient')

    def __str__(self):
        return f'Appointment(id={self.id}, status={self.status})'

    def reject(self):
        self.status = self.REJECTED
        self.save()

    @classmethod
    def find_in_date_range(cls, since=None, until=None):
        return cls._find_in_date_range(cls.appt_date, since, until)


class Doctor(BaseProfile):
    def __str__(self):
        return f'Doctor(id={self.pk}, surname={self.surname})'


class Patient(BaseProfile):

    age = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    number_of_teeth = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(32)]
    )
    number_of_surgeries = models.PositiveIntegerField()

    def __str__(self):
        return f'Patient(id={self.pk}, surname={self.surname})'
