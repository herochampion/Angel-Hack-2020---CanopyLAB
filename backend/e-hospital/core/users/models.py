from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

class HospitalUser(AbstractUser):
    first_name = models.TextField(null=True, blank=True)
    last_name = models.TextField(null=True, blank=True)
    bio = models.TextField(blank=True)
    location = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    health_status = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    servere_value = models.TextField(null=True, blank=True)
    medicince_list = models.TextField(null=True, blank=True)
    doctor_story = models.TextField(null=True, blank=True)
    role = models.TextField(null=False, default="patient")

class DoctorWorkSchedule(models.Model):
    user = models.ForeignKey(
        HospitalUser,
        on_delete=models.CASCADE,
        null=False
    )
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)

class LoginHistory(models.Model):
    user = models.ForeignKey(
        HospitalUser,
        on_delete=models.CASCADE,
        null=False
    )
    date = models.DateTimeField(null=False)
