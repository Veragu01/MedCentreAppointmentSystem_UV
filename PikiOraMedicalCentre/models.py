from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Appointment(BaseModel):
    reason = models.CharField(max_length=255, blank=True, null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_appointments")
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="doctor_appointments")
    date = models.DateField(blank=True, null=True)
    time_slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE, related_name="appointment_timeslot")

    def __str__(self):
        return "Appointment for: " + self.patient.first_name + " " + self.patient.last_name


class TimeSlot(BaseModel):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.time.strftime("%H:%M")

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
