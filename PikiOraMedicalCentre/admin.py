from django.contrib import admin

from PikiOraMedicalCentre.models import Appointment, TimeSlot, Profile

# Register your models here.
admin.site.register(Appointment)
admin.site.register(TimeSlot)
admin.site.register(Profile)