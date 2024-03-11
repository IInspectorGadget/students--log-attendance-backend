from rest_framework.permissions import BasePermission
from .models import Student, Teacher

class IsTeacherOrHeadman(BasePermission):
    def has_permission(self, request, view):
        # Проверяем, является ли пользователь учителем или студентом с isHeadman
        return request.user.is_authenticated and (request.user.user_type == '2' or request.user.student.isHeadman)

    def has_object_permission(self, request, view, obj):
        # Проверяем, является ли пользователь учителем или студентом с isHeadman для конкретного объекта (например, Attendance)
        return request.user.is_authenticated and (request.user.user_type == '2' or request.user.student.isHeadman)

class IsTeacher(BasePermission):
    """
    Проверяет, является ли пользователь аутентифицированным и учителем.
    """
    def has_permission(self, request, view):
        # Проверяем, является ли пользователь аутентифицированным
        if not request.user.is_authenticated:
            return False

        # Проверяем, является ли пользователь учителем
        try:
            teacher = Teacher.objects.get(user_id=request.user)
            return True
        except Teacher.DoesNotExist:
            return False
        
class IsStudent(BasePermission):
    """
    Проверяет, является ли пользователь аутентифицированным и студентом.
    """
    def has_permission(self, request, view):
        # Проверяем, является ли пользователь аутентифицированным
        if not request.user.is_authenticated:
            return False

        # Проверяем, является ли пользователь учителем
        try:
            student = Student.objects.get(user_id=request.user)
            return True
        except Student.DoesNotExist:
            return False