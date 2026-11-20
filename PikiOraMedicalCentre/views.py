from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

from rest_framework import serializers, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from PikiOraMedicalCentre.forms import AppointmentCreateForm, AppointmentUpdateForm, UserCreationForm, UserUpdateForm, \
    CreateTimeSlotFormDoctor, CreateTimeSlotFormAdmin, TimeSlotUpdateForm
from PikiOraMedicalCentre.models import Appointment, TimeSlot, Profile
from PikiOraMedicalCentre.serializers import DoctorSerializer, AppointmentSerializer, TimeSlotSerializer, \
    TimeSlotCreateSerializer, AppointmentCreateSerializer, AdminUserSerializer


# Create your views here.

def home(request):
    return render(request, 'PikiOraMedicalCentre/home.html')

# Appointments
def appointments(request):
    appointments = Appointment.objects.all()
    return render(request, 'PikiOraMedicalCentre/appointments.html', {'appointments': appointments})

def appointment_detail(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    return render(request, 'PikiOraMedicalCentre/appointment_detail.html', {'appointment': appointment})

def appointment_create(request):
    appointment_reason = request.POST.get('reason')
    appointment_time = request.POST.get('time_slot')
    appointment_patient = request.user
    appointment_doctor = request.POST.get('doctor')
    appointment_date = request.POST.get('date')
    appointment = Appointment.objects.create(patient=appointment_patient, reason=appointment_reason, time_slot_id=appointment_time, doctor_id=appointment_doctor, date=appointment_date)
    return render(request, 'PikiOraMedicalCentre/appointment_create_view.html', {'appointment': appointment})

def appointment_update(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    appointment.reason = request.POST.get('reason')
    appointment.time = request.POST.get('time')
    appointment.save()
    return redirect('appointments')

def appointment_delete(request):
    appointment_id = request.POST.get('appointment_id')
    appointment = Appointment.objects.get(id=appointment_id)
    appointment.delete()
    return redirect('appointments')

# Timeslots
def timeslot_detail(request, timeslot_id):
    timeslot = TimeSlot.objects.get(id=timeslot_id)
    return render(request, 'PikiOraMedicalCentre/timeslot_detail.html', {'timeslot': timeslot})

def timeslots(request):
    timeslots = TimeSlot.objects.all()
    return render(request, 'PikiOraMedicalCentre/timeslots.html', {'timeslots': timeslots})

def get_timeslots(request):
    doctor_id = request.GET.get('doctor_id')
    timeslots = TimeSlot.objects.filter(doctor_id=doctor_id).values("id", "date", "time", "is_available")
    return JsonResponse(list(timeslots), safe=False)

def timeslot_create(request):
    timeslot = TimeSlot.objects.create()
    return render(request, 'PikiOraMedicalCentre/timeslot_create.html', {'timeslot': timeslot})

def timeslot_delete(request):
    timeslot_id = request.POST.get('timeslot_id')
    timeslot = TimeSlot.objects.get(id=timeslot_id)
    timeslot.delete()
    return redirect('timeslots')

# Profiles
def register(request):
    username = request.POST['username']
    password = request.POST['password']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    phone = request.POST['phone']
    address = request.POST['address']
    email = request.POST['email']
    user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email)
    user.set_password(password)
    user.groups.add(2) # Patients group id=2
    user.save()
    Profile.objects.create(user=user, phone=phone, address=address)
    return redirect('login')

def register_doctor(request):
    username = request.POST['username']
    password = request.POST['password']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    phone = request.POST['phone']
    address = request.POST['address']
    email = request.POST['email']
    user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email)
    user.set_password(password)
    user.groups.add(1) # Doctors group id=1
    user.save()
    Profile.objects.create(user=user, phone=phone, address=address)
    return redirect('login')


def register_view(request):
    return render(request, 'PikiOraMedicalCentre/register.html')

def available_time_slots(request):
    doctor_id = request.GET.get('doctor')
    selected_date = request.GET.get('date')

    slots = TimeSlot.objects.filter(doctor_id=doctor_id, date=selected_date, is_available=True).order_by('time')

    data = [
        {'id': slot.id, 'label': slot.time.strftime('%H:%M'),}
        for slot in slots
    ]
    return JsonResponse({'time_slots': data})



# Generic Views
class AppointmentList_Generic(ListView):
    model = Appointment
    template_name = 'PikiOraMedicalCentre/appointments_list_view.html'

class AppointmentDetail_Generic(DetailView):
    model = Appointment
    template_name = 'PikiOraMedicalCentre/appointment_details_view.html'

class AppointmentCreate_Generic(CreateView):
    model = Appointment
    template_name = 'PikiOraMedicalCentre/appointment_create_view.html'
    success_url = '/appointments'
    form_class = AppointmentCreateForm

    def form_valid(self, form):
        time_slot = form.cleaned_data['time_slot']

        if not time_slot.is_available:
            form.add_error('time_slot', 'This timeslot is not available')
            return super().form_invalid(form)

        form.instance.patient = self.request.user
        response = super().form_valid(form)

        time_slot.is_available = False
        time_slot.save(update_fields=['is_available'])

        return response



class AppointmentUpdate_Generic(UpdateView):
    model = Appointment
    template_name = 'PikiOraMedicalCentre/appointment_update_view.html'
    success_url = '/appointments'
    form_class = AppointmentCreateForm

    def form_valid(self, form):
        appointment = self.get_object()

        old_time_slot_id = appointment.time_slot.id
        # old_time_slot_id = self.object.time_slot_id
        new_time_slot = form.cleaned_data['time_slot']
        new_time_slot_id = new_time_slot.id

        if old_time_slot_id != new_time_slot_id:
            if not new_time_slot.is_available:
                form.add_error(
                    'time_slot',
                    'This timeslot is not available'
                )
                return self.form_invalid(form)

        # form.instance.patient = self.request.user

        TimeSlot.objects.filter(id=old_time_slot_id).update(is_available=True)
        TimeSlot.objects.filter(id=new_time_slot_id).update(is_available=False)

        return super().form_valid(form)

class AppointmentDelete_Generic(DeleteView):
    model = Appointment
    template_name = 'PikiOraMedicalCentre/appointment_delete_view.html'
    success_url = '/appointments'

    def get_success_url(self):
        TimeSlot.objects.filter(id=self.object.time_slot.id).update(is_available=True)
        return reverse('appointments')

class TimeslotList_Generic(ListView):
    model = TimeSlot
    template_name = 'PikiOraMedicalCentre/timeslots_list_view.html'

class TimeslotDetail_Generic(DetailView):
    model = TimeSlot
    template_name = 'PikiOraMedicalCentre/timeslot_details_view.html'


class TimeslotCreate_Generic(CreateView):
    model = TimeSlot
    template_name = 'PikiOraMedicalCentre/timeslot_create_view.html'
    success_url = '/timeslots'

    def form_valid(self, form):
        doctor = self.request.user
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']

        # if current user is a doctor, check if timeslot is already taken
        if doctor== self.request.user.groups.filter(name='Doctors'):
            if TimeSlot.objects.filter(date=date, time=time, doctor=doctor).exists():
                form.add_error('time', 'This timeslot is already taken')
                return self.form_invalid(form)
            form.instance.doctor = doctor
        # else if current user is an administrator, assign doctor to selected doctor and check if timeslot is already taken
        elif self.request.user.groups.filter(name='Administrators').exists():
            doctor = form.cleaned_data['doctor']
            if TimeSlot.objects.filter(date=date, time=time, doctor=doctor).exists():
                form.add_error('time', 'This timeslot is already taken')
                return self.form_invalid(form)

        return super().form_valid(form)

    # if current user is an administrator, use CreateTimeSlotFormAdmin form, else use CreateTimeSlotFormDoctor form
    def get_form_class(self):
        if self.request.user.groups.filter(name='Administrators').exists():
            return CreateTimeSlotFormAdmin
        return CreateTimeSlotFormDoctor

class TimeslotUpdate_Generic(UpdateView):
    model = TimeSlot
    template_name = 'PikiOraMedicalCentre/timeslot_update_view.html'
    success_url = '/timeslots'
    form_class = TimeSlotUpdateForm

    def form_valid(self, form):
        old_time_slot = self.get_object()

        old_time_slot_id = old_time_slot.id


        doctor = old_time_slot.doctor
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']
        is_available = form.cleaned_data['is_available']

        if TimeSlot.objects.filter(date=date, time=time, doctor=doctor).exists():
            form.add_error('time', 'This timeslot is already taken')
            return self.form_invalid(form)

        TimeSlot.objects.filter(id=old_time_slot_id).update(is_available=is_available)
        TimeSlot.objects.filter(id=old_time_slot_id).update(date=date)
        TimeSlot.objects.filter(id=old_time_slot_id).update(time=time)

        return super().form_valid(form)

class TimeslotDelete_Generic(DeleteView):
    model = TimeSlot
    template_name = 'PikiOraMedicalCentre/timeslot_delete_view.html'

class PatientList_Generic(ListView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/patient_list_view.html'

class PatientCreate_Generic(CreateView):
    model = User
    template_name = 'PikiOraMedicalCentre/patient_create_view.html'

class PatientDetail_Generic(DetailView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/patient_details_view.html'

class PatientUpdate_Generic(UpdateView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/patient_update_view.html'
    success_url = '/patients'
    form_class = UserUpdateForm

class PatientDelete_Generic(DeleteView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/patient_delete_view.html'

class RegisterView_Generic(CreateView):
    # model = User
    template_name = 'PikiOraMedicalCentre/register.html'
    form_class = UserCreationForm
    success_url = '/login'


class DoctorList_Generic(ListView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/doctor_list_view.html'

    def get_queryset(self):
        doctors = Profile.objects.select_related("user").filter(user__groups__name='Doctors').distinct()
        print(doctors.count())
        print("Doctors:", [doctor.user.username for doctor in doctors])
        return doctors

class DoctorDetail_Generic(DetailView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/doctor_detail_view.html'

class DoctorDelete_Generic(DeleteView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/doctor_delete_view.html'


    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Doctors').exists():
            return reverse('home')
        elif user.groups.filter(name='Administrators').exists():
            return reverse('doctors')


class DoctorCreate_Generic(CreateView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/doctor_create_view.html'
    success_url = '/home'
    form_class = UserCreationForm

class DoctorUpdate_Generic(UpdateView):
    model = Profile
    template_name = 'PikiOraMedicalCentre/doctor_update_view.html'
    success_url = reverse_lazy("home")
    form_class = UserUpdateForm

    def get_object(self):
        return Profile.objects.get(pk=self.kwargs["pk"])

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['instance'] = self.get_object().user
    #     return kwargs

    def form_valid(self, form):
        # form.instance = self.request.user
        profile = self.get_object()
        user = profile.user

        user.username = form.cleaned_data["username"]
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        user.save()

        profile.phone = form.cleaned_data["phone"]
        profile.address = form.cleaned_data["address"]
        profile.user.email = form.cleaned_data["email"]
        profile.save()

        return redirect(self.success_url)

class DoctorListAPIView(generics.ListAPIView):
    serializer_class = DoctorSerializer

    def get_queryset(self):
        doctors = Profile.objects.select_related("user").filter(user__groups__name='Doctors').distinct()
        return doctors

class AppointmentListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="Administrators").exists():
            return Appointment.objects.select_related(
                "patient", "doctor", "time_slot"
            ).all()

        if user.groups.filter(name="Doctors").exists():
            return Appointment.objects.filter(doctor=user).select_related(
                "patient", "doctor", "time_slot"
            )

        # Default to patient access: only their own appointments.
        return Appointment.objects.filter(patient=user).select_related(
            "patient", "doctor", "time_slot"
        )


class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name="Administrators").exists():
            return Appointment.objects.select_related("patient", "doctor", "time_slot")

        if user.groups.filter(name="Doctors").exists():
            return Appointment.objects.filter(doctor=user).select_related("patient", "doctor", "time_slot")

        return Appointment.objects.filter(patient=user).select_related("patient", "doctor", "time_slot")

    def perform_destroy(self, instance):
        with transaction.atomic():
            appointment = Appointment.objects.select_for_update().get(pk=instance.pk)
            slot = TimeSlot.objects.select_for_update().get(pk=appointment.time_slot_id)
            slot.is_available = True
            slot.save(update_fields=["is_available"])
            appointment.delete()

class TimeslotAPIView(generics.ListAPIView):
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        doctor_id = self.request.query_params.get("doctor")
        date = self.request.query_params.get("date")

        slots = TimeSlot.objects.select_related("doctor")

        # print("All slots:", slots.count())
        # print("Available slots:", slots.filter(is_available=True).count())
        # print("Requested doctor:", repr(doctor_id))
        # print("Requested date:", repr(date))

        print(
            "Doctor IDs on slots:",
            list(
                TimeSlot.objects.values_list("doctor_id", flat=True)
                .distinct()
            )
        )
        print(
            "Slots for doctor 8:",
            list(
                TimeSlot.objects.filter(doctor_id=8)
                .values("id", "date", "time", "is_available")
            )
        )

        if user.groups.filter(name="Administrators").exists():
            pass
        elif user.groups.filter(name="Doctors").exists():
            slots = slots.filter(doctor=user)

        elif user.groups.filter(name="Patients").exists():
            slots = slots.filter(is_available=True)
        else:
            return TimeSlot.objects.none()
        if doctor_id and not user.groups.filter(name="Doctors").exists():
            slots = slots.filter(doctor_id=doctor_id)
            print("After doctor filter:", slots.count())


        if date:
            slots = slots.filter(date=date)
            print("After date filter:", slots.count())

        print("Final matches:", list(slots.values("id", "doctor_id", "date", "time", "is_available")))
        return slots.order_by("time")
    # def get_queryset(self):
    #     # timeslotRequest = TimeSlot.objects.filter(is_available=True).select_related("doctor").distinct()
    #     doctor_id = self.request.query_params.get("doctor")
    #     # date = self.request.query_params.get("date")
    #     available_slots = TimeSlot.objects.filter(is_available=True)
    #     user = self.request.user
    #
    #     if user.groups.filter(name="Doctors").exists():
    #         return available_slots.filter(doctor_id=user).order_by("date", "time")
    #
    #     if user.groups.filter(name="Administrators").exists():
    #         return available_slots.order_by("date", "time")
    #
    #     return TimeSlot.objects.none()

        # if not doctor_id or not date:
        #     return timeslotRequest.none()
        # return timeslotRequest.filter(doctor_id=doctor_id, date=date).order_by("time")
        # # if date:
        # #     timeslotRequest = timeslotRequest.filter(date=date)
        # # return timeslotRequest.order_by("date", "time")



class TimeslotDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeSlotSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        slots = TimeSlot.objects.select_related("doctor")

        if user.groups.filter(name="Administrators").exists():
            return slots

        if user.groups.filter(name="Doctors").exists():
            return slots.filter(doctor=user)

        return TimeSlot.objects.none()

    def perform_destroy(self, instance):
        instance.delete()


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        groups = set(user.groups.values_list("name", flat=True))

        if "Administrators" in groups:
            user_type = "administrator"
        elif "Doctors" in groups:
            user_type = "doctor"
        elif "Patients" in groups:
            user_type = "patient"
        else:
            user_type = ""

        return Response({"token": token.key, "user_type": user_type, "first_name": user.first_name, "last_name": user.last_name,})


class TimeslotCreateAPIView(generics.CreateAPIView):
    serializer_class = TimeSlotCreateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.groups.filter(name="Doctors").exists():
            raise PermissionDenied("Only doctors can create timeslots.")

        serializer.save(doctor=self.request.user, is_available=True)

class AppointmentCreateAPIView(generics.CreateAPIView):
    serializer_class = AppointmentCreateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Administrators").exists()
        )


class AdminUserListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdministrator]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return User.objects.filter(
            groups__name__in=["Doctors", "Patients"]
        ).distinct()


class AdminUserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdministrator]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return User.objects.filter(
            groups__name__in=["Doctors", "Patients"]
        ).distinct()