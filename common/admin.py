from django.contrib import admin

from .models import Speciality, Polyclinic, Room, Enrollment, WorkTime

admin.site.register(Speciality)
admin.site.register(Polyclinic)
admin.site.register(Room)
admin.site.register(Enrollment)
admin.site.register(WorkTime)
