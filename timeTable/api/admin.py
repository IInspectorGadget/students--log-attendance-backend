from django.contrib import admin
# Register your models here.
from .models import *

admin.site.register(CustomUser)
admin.site.register(Teacher)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(SubjectRealization)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
