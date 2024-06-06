from django.contrib import admin, messages
from django.urls import path, reverse
# Register your models here.
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from django import forms
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.forms import UserChangeForm,UserCreationForm,AdminPasswordChangeForm
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())
        

class UserAdmin(admin.ModelAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None
    form = UserChangeForm

    fieldsets = (
        ("Учётный данные", {"fields": ("username", "password")}),
        (
          "Личная информация",
          {
              "classes": ("wide",),
              "fields": ("first_name", "last_name", "middle_name", "phone","email"),
          },
        ),
        (
          _("Permissions"),
          {
              "fields": (
                  "is_active",
                  "is_staff",
                  "is_superuser",
                  "groups",
                  "user_permissions",
              ),
          },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "Регистрация",
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "user_type"),
            },
        ),
        (
            "Личная информация",
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "middle_name", "phone","email"),
            },
        ),
        (
             _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        )
    )
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)
    
    list_display = ("username",  "user_type", "first_name", "last_name","middle_name", "email","phone","is_staff")
    list_filter = ("user_type", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username",  "user_type", "first_name", "last_name","middle_name", "email","phone")
    ordering = ("first_name", "last_name","middle_name",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def get_urls(self):
        return [
            path(
                "<id>/password/",
                self.admin_site.admin_view(self.user_change_password),
                name="auth_user_password_change",
            ),
        ] + super().get_urls()
    
    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=""):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {
                    "name": self.opts.verbose_name,
                    "key": escape(id),
                }
            )
        if request.method == "POST":
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext("Password changed successfully.")
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_change"
                        % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Change password: %s") % escape(user.get_username()),
            "adminForm": admin_form,
            "form_url": form_url,
            "form": form,
            "is_popup": (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            "is_popup_var": IS_POPUP_VAR,
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.opts,
            "original": user,
            "save_as": False,
            "show_save": True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template
            or "admin/auth/user/change_password.html",
            context,
        )

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'get_email','get_phone',)
    search_fields = ("user_id__first_name", "user_id__last_name","user_id__middle_name", "user_id__email","user_id__phone")


    def get_email(self, obj):
        return obj.user_id.email
    def get_phone(self, obj):
        return obj.user_id.phone
    get_email.short_description = 'Почти'
    get_phone.short_description = 'Телефон'

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'get_email','get_phone','isHeadman','get_group')
    list_filter = ('group_id__name','isHeadman')
    search_fields = ("user_id__first_name", "user_id__last_name","user_id__middle_name", "user_id__email","user_id__phone")
    def get_email(self, obj):
        return obj.user_id.email
    def get_phone(self, obj):
        return obj.user_id.phone
    def get_group(self, obj):
        return obj.group_id.name  
    get_group.short_description = 'Группа'
    get_email.short_description = 'Почти'
    get_phone.short_description = 'Телефон'

class StudentInline(admin.TabularInline):
    model = Student
    extra = 0


class AttendanceReportInline(admin.TabularInline):
    model = AttendanceReport
    extra = 0

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_students',)  # Отображаем имя группы и список студентов
  
    def display_students(self, obj):
        students = obj.student_set.all()
        return ", ".join([student.user_id.get_full_name() for student in students])

    display_students.short_description = 'Студенты'  # Название столбца в админ панели

    inlines = [
        StudentInline,
    ]

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name',) 
    search_fields= ('name', )

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name','get_faculty') 
    search_fields= ('name', 'faculty_id__name' )

    @admin.display(
            ordering="faculty_id__name",
            description="Факультет",
    )
    def get_faculty(self,obj):
        return obj.faculty_id.name

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',) 
    search_fields= ('name', )


class SubjectRealizationAdmin(admin.ModelAdmin):
    list_display = ('type','get_subject', 'teacher_id') 
    search_fields= ('type', 
                    'teacher_id__user_id__last_name',
                    'teacher_id__user_id__first_name',
                    'teacher_id__user_id__middle_name' 
                    )
    list_filter = ("type",)

    @admin.display(
            ordering="subject_id__name",
            description="Предмет",
    )
    def get_subject(self,obj):
        return obj.subject_id.name
    
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_subject','get_teacher','get_teacher_replacement','location','date','time_start','time_end','display_groups','isComplete') 
    search_fields= ('subject_realization_id__subject_id__name', 
                    'subject_realization_id__teacher_id__user_id__first_name',
                    'subject_realization_id__teacher_id__user_id__middle_name',
                    'subject_realization_id__teacher_id__user_id__last_name',
                    'teacher_replacement__user_id__first_name',
                    'teacher_replacement__user_id__middle_name',
                    'teacher_replacement__user_id__last_name',
                    'location',
                    'date',
                    'time_start',
                    'time_end'
                    )
    list_filter = ('groups','isComplete') 

    inlines = [
        AttendanceReportInline,
    ]

    @admin.display(
            description="группы",
    )
    def display_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    @admin.display(
            ordering="subject_realization_id__subject_id__name",
            description="Предмет",
    )
    def get_subject(self,obj):
        return obj.subject_realization_id.subject_id.name
    
    @admin.display(
            ordering="subject_realization_id__teacher_id",
            description="Преподаватель",
    )
    def get_teacher(self,obj):
        return obj.subject_realization_id.teacher_id

    @admin.display(
            ordering="teacher_replacement",
            description="Заменяет",
    )
    def get_teacher_replacement(self,obj):
        return obj.teacher_replacement

class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('student_id',
                    'get_subject',
                    'get_teacher',
                    'get_teacher_replacement',
                    'last_edit_time',
                    'get_my_status_display',
                    'get_date',
                    'get_time_start'
                  ) 
    search_fields= (
        'student_id__user_id__first_name',
        'student_id__user_id__last_name',
        'student_id__user_id__middle_name',
        'attendance_id__subject_realization_id__subject_id__name',
        'attendance_id__subject_realization_id__teacher_id__user_id__first_name',
        'attendance_id__subject_realization_id__teacher_id__user_id__last_name',
        'attendance_id__subject_realization_id__teacher_id__user_id__middle_name',
        'attendance_id__date',
        'attendance_id__time_start',
        'last_edit_time',
        )
    list_filter = ('status',)

    @admin.display(
            ordering="attendance_id__subject_realization_id__subject_id__name",
            description="Предмет",
    )
    def get_subject(self,obj):
        return obj.attendance_id.subject_realization_id.subject_id.name
    
    @admin.display(
            ordering="attendance_id__subject_realization_id__teacher_id",
            description="Преподаватель",
    )
    def get_teacher(self,obj):
        return obj.attendance_id.subject_realization_id.teacher_id

    @admin.display(
            ordering="attendance_id__teacher_replacement",
            description="Заменяет",
    )
    def get_teacher_replacement(self,obj):
        return obj.attendance_id.teacher_replacement
    
    @admin.display(
            ordering="status",
            description="Статус",
    )
    def get_my_status_display(self,obj):
        return obj.get_status_display()
    
    @admin.display(
            ordering="attendance_id__date",
            description="Дата",
    )
    def get_date(self,obj):
        return str(obj.attendance_id.date) 
    
    @admin.display(
            ordering="attendance_id__time_start",
            description="Время начала",
    )
    def get_time_start(self,obj):
        return str(obj.attendance_id.time_start) 
    
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectRealization, SubjectRealizationAdmin)
admin.site.register(Attendance,AttendanceAdmin)
admin.site.register(AttendanceReport, AttendanceReportAdmin)
