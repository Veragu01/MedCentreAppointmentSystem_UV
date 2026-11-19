from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework import serializers

from .models import Appointment, TimeSlot, Profile


class DoctorSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Profile
        fields = ["user_id", "first_name", "last_name", "phone"]


class TimeSlotSerializer(serializers.ModelSerializer):
    doctor_first_name = serializers.CharField(source="doctor.first_name", read_only=True)
    doctor_last_name = serializers.CharField(source="doctor.last_name", read_only=True)

    class Meta:
        model = TimeSlot
        fields = ["id",
                  "doctor",
                  "date",
                  "time",
                  "is_available",
                  "doctor",
                  "doctor_first_name",
                  "doctor_last_name",]


class TimeSlotCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ["id", "date", "time", "is_available"]
        read_only_fields = ["id", "is_available"]



class AppointmentSerializer(serializers.ModelSerializer):
    patient_first_name = serializers.CharField(source="patient.first_name", read_only=True)
    patient_last_name = serializers.CharField(source="patient.last_name", read_only=True)
    doctor_first_name = serializers.CharField(source="doctor.first_name", read_only=True)
    doctor_last_name = serializers.CharField(source="doctor.last_name", read_only=True)
    time_slot_time = serializers.CharField(source="time_slot.time", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_first_name",
            "patient_last_name",
            "doctor",
            "doctor_first_name",
            "doctor_last_name",
            "date",
            "time_slot_time",
            "reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

        def validate(self, attrs):
            if not self.instance:
                return attrs

            slot = attrs.get("time_slot", self.instance.time_slot)
            appointment_date = attrs.get("date", self.instance.date)

            if slot.doctor_id != self.instance.doctor_id:
                raise serializers.ValidationError(
                    {"time_slot": "Choose a slot belonging to this appointment's doctor."}
                )

            if slot.date != appointment_date:
                raise serializers.ValidationError(
                    {"date": "The appointment date must match the selected time slot."}
                )

            if slot.pk != self.instance.time_slot_id and not slot.is_available:
                raise serializers.ValidationError(
                    {"time_slot": "That time slot is no longer available."}
                )

            return attrs

        def update(self, instance, validated_data):
            with transaction.atomic():
                appointment = Appointment.objects.select_for_update().get(pk=instance.pk)
                requested_slot = validated_data.get("time_slot", appointment.time_slot)

                slot_ids = sorted({appointment.time_slot_id, requested_slot.pk})
                locked_slots = {
                    slot.pk: slot
                    for slot in TimeSlot.objects.select_for_update()
                    .filter(pk__in=slot_ids)
                    .order_by("pk")
                }

                old_slot = locked_slots[appointment.time_slot_id]
                new_slot = locked_slots[requested_slot.pk]

                if new_slot.doctor_id != appointment.doctor_id:
                    raise serializers.ValidationError(
                        {"time_slot": "Choose a slot belonging to this appointment's doctor."}
                    )

                new_date = validated_data.get("date", appointment.date)
                if new_slot.date != new_date:
                    raise serializers.ValidationError(
                        {"date": "The appointment date must match the selected time slot."}
                    )

                if new_slot.pk != old_slot.pk:
                    if not new_slot.is_available:
                        raise serializers.ValidationError(
                            {"time_slot": "That time slot is no longer available."}
                        )
                    old_slot.is_available = True
                    new_slot.is_available = False
                    old_slot.save(update_fields=["is_available"])
                    new_slot.save(update_fields=["is_available"])

                appointment.date = new_date
                appointment.time_slot = new_slot
                appointment.reason = validated_data.get("reason", appointment.reason)
                appointment.save(update_fields=["date", "time_slot", "reason", "updated_at"])

                return appointment


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    class Meta:
        model = Profile
        fields = ["id", "user", "first_name", "last_name", "phone", "address"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    time_slot = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all()
    )

    class Meta:
        model = Appointment
        fields = ["id", "time_slot", "reason", "date", "doctor", "patient"]
        read_only_fields = ["id", "doctor", "patient"]

    def create(self, validated_data):
        patient = validated_data.pop("patient")
        submitted_slot = validated_data.pop("time_slot")

        with transaction.atomic():
            slot = TimeSlot.objects.select_for_update().get(pk=submitted_slot.pk)

            if not slot.is_available:
                raise serializers.ValidationError({
                    "time_slot": "This time slot is no longer available."
                })

            appointment = Appointment.objects.create(patient=patient, doctor=slot.doctor, date=slot.date, time_slot=slot, **validated_data )

            slot.is_available = False
            slot.save(update_fields=["is_available"])

        return appointment

class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=["doctor", "patient"], write_only=True, required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "password", "first_name", "last_name",
            "email", "role", "phone", "address",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, data):
        role = data.pop("role")
        phone = data.pop("phone", "")
        address = data.pop("address", "")

        user = User.objects.create_user(**data)
        Profile.objects.create(user=user, phone=phone, address=address)

        group_name = "Doctors" if role == "doctor" else "Patients"
        user.groups.add(Group.objects.get(name=group_name))
        return user

    def to_representation(self, user):
        data = super().to_representation(user)
        data["phone"] = user.profile.phone
        data["address"] = user.profile.address

        if user.groups.filter(name="Patients").exists():
            data["role"] = "patient"
        elif user.groups.filter(name="Doctors").exists():
            data["role"] = "doctor"
        else:
            data["role"] = ""

        return data

    def update(self, user, data):
        phone = data.pop("phone", None)
        address = data.pop("address", None)
        role = data.pop("role", None)

        for field, value in data.items():
            setattr(user, field, value)
        user.save()

        profile = user.profile
        if phone is not None:
            profile.phone = phone
        if address is not None:
            profile.address = address
        if phone is not None or address is not None:
            profile.save()

        if role:
            if role == "doctor":
                group_name = "Doctors"
            else:
                group_name = "Patients"
            user.groups.set([Group.objects.get(name=group_name)])

        return user
