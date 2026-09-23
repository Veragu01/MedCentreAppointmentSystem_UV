from datetime import date

from django import forms
from django.contrib.auth.models import User

from PikiOraMedicalCentre.models import Appointment, TimeSlot, Profile


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
    phone = forms.CharField(required=True, widget=forms.NumberInput(attrs={"class": "form-control", "style": "width: 75%"}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control", "style": "width: 200%"}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', "style": "width: 150%"}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        help_texts = {'username': None}


class UserUpdateForm(forms.ModelForm):
    phone = forms.CharField(required=True, widget=forms.NumberInput(attrs={"class": "form-control", "style": "width: 75%"}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control", "style": "width: 200%"}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', "style": "width: 150%"}),
        }
        help_texts = {'username': None}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        profile = self.instance
        selected_user = profile.user

        self.fields["username"].initial = selected_user.username
        self.fields["first_name"].initial = selected_user.first_name
        self.fields["last_name"].initial = selected_user.last_name
        self.fields["email"].initial = selected_user.email
        self.fields["phone"].initial = profile.phone
        self.fields["address"].initial = profile.address



