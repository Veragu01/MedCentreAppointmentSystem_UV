from datetime import date

from django import forms
from django.contrib.auth.models import User

from PikiOraMedicalCentre.models import Appointment, TimeSlot


# from PikiOraMedicalCentre.views import TimeSlot


class AppointmentCreateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['reason', 'doctor', 'date', 'time_slot']
        widgets ={
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        doctors = User.objects.filter(groups__name="Doctors").distinct()

        self.fields["doctor"].queryset = doctors
        self.fields["doctor"].label_from_instance = self.doctor_label

        self.fields["time_slot"].queryset = TimeSlot.objects.none()
        doctor_id = self.data.get("doctor")
        selected_date = self.data.get("date")

        if doctor_id and selected_date:
            self.fields["time_slot"].queryset = TimeSlot.objects.filter(
                doctor_id=doctor_id,
                date=selected_date,
                is_available=True).order_by("time")

    def doctor_label(self, doctor):
        return f"{doctor.first_name + " " + doctor.last_name}"

class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['reason', 'doctor', 'date', 'time_slot']
        widgets ={
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        doctors = User.objects.filter(groups__name="Doctors").distinct()

        self.fields["doctor"].queryset = doctors
        self.fields["doctor"].label_from_instance = self.doctor_label

        # self.fields["time_slot"].queryset = TimeSlot.objects.none()
        doctor_id = self.data.get("doctor")
        selected_date = self.data.get("date")

        if doctor_id and selected_date:
            self.fields["time_slot"].queryset = TimeSlot.objects.filter(
                doctor_id=doctor_id,
                date=selected_date,
                is_available=True).order_by("time")

    def doctor_label(self, doctor):
        return f"{doctor.first_name + " " + doctor.last_name}"

class UserCreationForm(forms.ModelForm):
    phone = forms.CharField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        