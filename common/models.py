from django.db import models
from django.core.exceptions import ValidationError

class Speciality(models.Model):
    title = models.CharField(max_length=40)

    def __str__(self):
        return self.title


class Polyclinic(models.Model):
    DISTRICT = (
        ('XR', 'Xorazm'),
        ('TH', 'Toshkent'),
        ('SM', 'Samarqand')
    )

    number = models.PositiveIntegerField()
    district = models.CharField(choices=DISTRICT, max_length=2)
    address = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.number}-Polyclinic, {self.district}"


class Room(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    number = models.PositiveIntegerField()
    floor = models.PositiveIntegerField()
    polyclinic = models.ForeignKey(Polyclinic, on_delete=models.CASCADE, related_name='room')

    def __str__(self):
        return f"{self.number}-room, {self.polyclinic}-Polyclinic"


def validate_work_time(value):
    if value.hour > 15 and value.hour < 9:
        raise ValidationError("xatolik shifokor ish vaqti emas")


class Enrollment(models.Model):
    patient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='patient_enrollment')
    doctor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='doctor_enrollment')
    start_etime = models.DateTimeField(validators=[validate_work_time])
    end_etime = models.DateTimeField(validators=[validate_work_time])

    create_at = models.DateTimeField(auto_now_add=True)

    @property
    def clinic(self):
        return self.patient.polyclinic

    polyclinic = clinic

    @property
    def doctor_room(self):
        return self.doctor.room

    room = doctor_room

    def __str__(self):
        return f"P: {self.patient.first_name}, D: {self.doctor.first_name}, {self.start_etime}"


def validate_during(value):
    if value > 45 and value < 10:
        raise ValidationError("Vaqtni 10 va 45 oraligida bering")
    return value


class WorkTime(models.Model):
    WEEK_DAYS = [
        (6, 'saturday'),
        (0, 'monday'),
        (1, 'tuesday'),
        (2, 'wednesday'),
        (3, 'thursday'),
        (4, 'friday'),
        (5, 'sunday')
    ]
    doctor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='work_time')
    weekday = models.IntegerField(choices=WEEK_DAYS, unique=True)
    start_work_time = models.TimeField()
    end_work_time = models.TimeField()
    during = models.PositiveIntegerField(validators=[validate_during])
    etimes = models.JSONField()

    def __str__(self):
        return f"{self.doctor_id}: {self.weekday}"


class Diagnosis(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='diagnosis')
    text = models.TextField()
