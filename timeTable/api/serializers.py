import json
from rest_framework import serializers
from .models import Attendance, AttendanceReport, CustomUser, Group, Student, Subject, SubjectRealization
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['middle_name'] = user.middle_name
        return token

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'middle_name', 'phone']  # Укажите нужные вам поля

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'username', 'password']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

class StudentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(source='user_id', read_only=True)  # В source указываем поле ForeignKey, связывающее Student и CustomUser

    class Meta:
        model = Student
        fields = ['id', 'user', 'group_id', 'isHeadman']  # Укажите нужные вам поля из модели Student

class AttendanceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.subject_realization_id.subject_id.name
        representation['type'] = instance.subject_realization_id.get_type_display()
        return representation
    
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'subject_realization_id', 'location', 'date', 'isComplete']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['time_start'] = instance.time_start.strftime('%H:%M')
        representation['time_end'] = instance.time_start.strftime('%H:%M')
        representation['subject'] = {
            "id": instance.subject_realization_id.subject_id.id,  
            "name": instance.subject_realization_id.subject_id.name
        }
        representation['type'] = {
            "id": instance.subject_realization_id.type, 
            "name" : instance.subject_realization_id.get_type_display()
        }
        representation['teacher'] = {
            "id" :instance.subject_realization_id.teacher_id.user_id.id,
            "first_name": instance.subject_realization_id.teacher_id.user_id.first_name,
            "last_name": instance.subject_realization_id.teacher_id.user_id.last_name,
            "middle_name": instance.subject_realization_id.teacher_id.user_id.middle_name,
        }

        groups = {}
        for group_id, group_name in instance.groups.values_list('id', 'name'):
            groups[group_id] = {
                'name': group_name,
            }
        representation['groups'] = groups

        if instance.teacher_replacement:
             representation['teacher_replacement'] = {
                "id": instance.teacher_replacement.user_id.id,
                "first_name": instance.teacher_replacement.user_id.first_name,
                "last_name": instance.teacher_replacement.user_id.last_name,
                "middle_name": instance.teacher_replacement.user_id.middle_name,
             }
        else:
             representation['teacher_replacement'] = ""

        groups = instance.groups.all()
        if groups.exists():
            group = groups.first()
            representation['faculty'] =  {
                "id":group.course_id.faculty_id.id,
                "name":group.course_id.faculty_id.name
            }
            representation['course'] =  {
                "id":group.course_id.id,
                "name":group.course_id.name
            }
    

        return representation

class AttendanceReportGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id"]
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["first_name"] =  instance.user_id.first_name
        representation["last_name"] = instance.user_id.last_name 
        representation["middle_name"] = instance.user_id.middle_name
        try:
            attendance_report = AttendanceReport.objects.get(student_id=instance.id, attendance_id=self.context["attendance_id"])
            representation['type'] = attendance_report.status
            representation['last_edit_time'] = attendance_report.last_edit_time.strftime('%H:%M')
        except AttendanceReport.DoesNotExist:
            representation['type'] = None
            representation['last_edit_time'] = None
        return representation
    
class AttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceReport
        fields = '__all__'

class SubjectRealizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectRealization
        fields = '__all__'
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['subject'] = {
            "id": instance.subject_id.id, 
            "name": instance.subject_id.name, 
        }
        representation['type'] = {
            "id": instance.type, 
            "name" : instance.get_type_display()
        }
        return representation
    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['course'] = instance.course_id.name
        representation['faculty'] = instance.course_id.faculty_id.name
        return representation
