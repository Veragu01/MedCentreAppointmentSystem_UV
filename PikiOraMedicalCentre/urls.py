from django.urls import path
from PikiOraMedicalCentre.views import home, appointments, appointment_detail, appointment_create, appointment_update, appointment_delete, timeslots, timeslot_detail, timeslot_create, timeslot_delete, register, register_view

urlpatterns = [
    path("", home, name='home'),

    path("appointments/", appointments, name="appointments"),

]