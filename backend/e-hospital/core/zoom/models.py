
# Create your models here.
from django.db import models
from core.users.models import HospitalUser
class Meeting(models.Model):
    uuid = models.TextField(null=True, blank=True)
    host_id = models.TextField(null=True, blank=True)
    topic = models.TextField(null=False, blank=False)
    status = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField()
    timezone = models.TextField(null=True, blank=True)
    agenda = models.TextField(null=True, blank=True)
    created_at = models.TextField(null=True, blank=True)
    start_url = models.TextField(null=True, blank=True)
    join_url = models.TextField(null=True, blank=True)
    zoomus_meeting_id = models.BigIntegerField(null=True, blank=True)
    user = models.ForeignKey(
        HospitalUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='user_meeting'
    )
    doctor = models.ForeignKey(
        HospitalUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='doctor_meeting'
    )
