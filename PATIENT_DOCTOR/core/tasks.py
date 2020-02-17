from celery import Celery, group

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Appointment
from PATIENT_DOCTOR.authentication.models import BaseProfile

app = Celery()


@app.task
def send_emails():
    emails = BaseProfile.objects.exclude(email='').values_list('email', flat=True).distinct()
    g = group(send_daily_email.s(email) for email in emails)
    g.apply_async()


@app.task
def send_daily_email(email):
    subject = "Daily message"
    message = "Have a nice day!"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


@app.task
def send_email_on_appointment_cancel(appt_date, appt_time, emails):
    subject = "Canceled appointment"
    message = f"Your appointment was canceled successfully at {appt_time}  on {appt_date}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails)


@app.task
def send_email_on_appointment_reschedule(appt_date, appt_time, emails):
    subject = "Rescheduled appointment"
    message = f"Your appointment was rescheduled at {appt_time}  on {appt_date}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails)


@app.task
def check_statuses():
    Appointment.objects.filter(
        status=Appointment.PENDING, appt_date__lte=timezone.now()
    ).update(
        status=Appointment.FINISHED
    )
