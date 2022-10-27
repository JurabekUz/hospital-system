from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from common.models import Polyclinic, Room, Speciality

phone_regex = RegexValidator(
    regex=r'^998[0-9]{9}$',
    message="Phone number must be entered in the format: '998 [XX] [XXX XX XX]'. Up to 12 digits allowed."
)

LEVEL = (
    ('oliy', 'Oliy'),
    ('1_toifa', '1-toifa'),
    ('2_toifa', '1-toifa')
)

DISTRICT = (
    ('XR', 'Xorazm'),
    ('TH', 'Toshkent'),
    ('SM', 'Samarqand')
)

class User(AbstractUser):
    created_at = models.DateTimeField(("date created"), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(("date updated"), auto_now=True)

    is_doctor = models.BooleanField(default=False)
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL,
                                   default=None, null=True, blank=True,
                                   related_name='doctor')
    polyclinic = models.ForeignKey(Polyclinic, on_delete=models.SET_NULL,
                                   default=None, null=True, blank=True,
                                   related_name='user')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL,
                             default=None, null=True, blank=True,
                             related_name='doctor')
    level = models.CharField(choices=LEVEL, max_length=10, default='2_toifa')

    district = models.CharField(choices=DISTRICT, max_length=2, default='XR')
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=12, validators=[phone_regex])
    passport = models.CharField(max_length=9)

    REQUIRED_FIELDS = ["first_name", 'last_name', 'address', 'phone_number', 'passport']

    def __str__(self):
        if self.is_doctor:
            return f"doctor {self.first_name}, {self.polyclinic}-polyclinic, {self.room}-room"
        return f"{self.username}: {self.last_name}"

    class Meta:
        db_table = "user"
        swappable = "AUTH_USER_MODEL"
        verbose_name = ("user")
        verbose_name_plural = ("users")


    def clean(self):
        cleaned_data = super().clean()
        if self.is_doctor and self.speciality and self.room and self.level:
            return cleaned_data
        else:
            return ValidationError({'error': "xatolik"})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)






