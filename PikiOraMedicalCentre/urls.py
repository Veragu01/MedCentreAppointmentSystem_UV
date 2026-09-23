from django.urls import path, include

from PikiOraMedicalCentre.views import home, appointments, appointment_detail, appointment_create, appointment_update, \
    appointment_delete, timeslots, timeslot_detail, timeslot_create, timeslot_delete, register, register_view, \
    AppointmentList_Generic, AppointmentDetail_Generic, AppointmentCreate_Generic, AppointmentUpdate_Generic, \
    AppointmentDelete_Generic, TimeslotList_Generic, TimeslotDetail_Generic, TimeslotCreate_Generic, \
    TimeslotDelete_Generic, get_timeslots, available_time_slots, RegisterView_Generic, DoctorList_Generic, \
    DoctorDetail_Generic, DoctorDelete_Generic, DoctorCreate_Generic, register_doctor, DoctorUpdate_Generic, \
    TimeslotUpdate_Generic, PatientList_Generic, PatientDetail_Generic, PatientUpdate_Generic, PatientDelete_Generic

urlpatterns = [
    path("", home, name='home'),

    path("appointments/", AppointmentList_Generic.as_view(), name="appointments"),

    path("appointment_details/<int:pk>/", AppointmentDetail_Generic.as_view(), name="appointment_details"),

    path("appointment_create/", AppointmentCreate_Generic.as_view(), name="appointment_create"),

    path("appointment_update/<int:pk>/", AppointmentUpdate_Generic.as_view(), name="appointment_update"),

    path("appointment_delete/<int:pk>/", AppointmentDelete_Generic.as_view(), name="appointment_delete"),

    path("timeslots/", TimeslotList_Generic.as_view(), name="timeslots"),

    path("timeslot_details/<int:pk>/", TimeslotDetail_Generic.as_view(), name="timeslot_details"),

    path("timeslot_create/", TimeslotCreate_Generic.as_view(), name="timeslot_create"),

    path("timeslot_update/<int:pk>/", TimeslotUpdate_Generic.as_view(), name="timeslot_update"),

    path("timeslot_delete/<int:pk>/", TimeslotDelete_Generic.as_view(), name="timeslot_delete"),

    path("get_timeslots/", get_timeslots, name="get_timeslots"),

    path('available-time-slots/', available_time_slots, name='available_time_slots'),

    path("register_form/", RegisterView_Generic.as_view(), name="register_form"),

    path("register/", register, name="register"),

    path("register_doctor/", register_doctor, name="register_doctor"),

    path("accounts/", include("django.contrib.auth.urls")),

    path("doctors/", DoctorList_Generic.as_view(), name="doctors"),

    path("doctor_details/<int:pk>/", DoctorDetail_Generic.as_view(), name="doctor_details"),

    path("doctor_delete/<int:pk>/", DoctorDelete_Generic.as_view(), name="doctor_delete"),

    path("doctor_create/", DoctorCreate_Generic.as_view(), name="doctor_create"),

    path("doctor_update/<int:pk>/", DoctorUpdate_Generic.as_view(), name="doctor_update"),

    path("patients/", PatientList_Generic.as_view(), name='patients'),

    path("patient_details/<int:pk>/", PatientDetail_Generic.as_view(), name="patient_details"),

    path("patient_update/<int:pk>/", PatientUpdate_Generic.as_view(), name="patient_update"),

    path("patient_delete/<int:pk>/", PatientDelete_Generic.as_view(), name="patient_delete"),
]
