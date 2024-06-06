import calendar
from datetime import date
import datetime
from math import inf
from re import search
from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from .permissions import IsTeacher, IsStudent, IsTeacherOrHeadman
from django.db.models import F
from django.db.models import Q
from .models import Attendance, AttendanceReport, Course, CustomUser, Faculty, Group, Student, Subject, SubjectRealization, Teacher
from .serializers import AttendanceReportGroupSerializer, AttendanceReportSerializer, AttendanceReportSerializerCRUD, AttendanceSerializer, AttendanceSerializer, AttendanceSerializerCRUD, AttendanceSimpleSerializer, CourseSerializerCRUD, CustomUserSerializer, CustomUserSerializerCRUD, FacultySerializerCRUD, GroupSerializer, GroupSerializerCRUD, StudentSerializer, StudentSerializerCRUD, SubjectRealization, SubjectRealizationSerializer, SubjectRealizationSerializerCRUD, SubjectSerializer, SubjectSerializerCRUD, TeacherSerializer, TeacherSerializerCRUD, UserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from rest_framework import viewsets

def is_student(user):
    """
    Функция для проверки, является ли пользователь студентом.
    
    Аргументы:
    user (CustomUser): Объект пользователя.

    Возвращает:
    bool: True, если пользователь является студентом, False в противном случае.
    """
    try:
        # Проверяем, есть ли ассоциированный объект Student у пользователя
        student = user.student
        # Если объект существует, возвращаем True
        return True
    except Student.DoesNotExist:
        # Если объект не существует, значит пользователь не является студентом
        return False
def is_teacher(user):
    """
    Функция для проверки, является ли пользователь учителем.
    
    Аргументы:
    user (CustomUser): Объект пользователя.

    Возвращает:
    bool: True, если пользователь является учителем, False в противном случае.
    """
    try:
        # Проверяем, есть ли ассоциированный объект Teacher у пользователя
        teacher = user.teacher
        # Если объект существует, возвращаем True
        return True
    except Teacher.DoesNotExist:
        # Если объект не существует, значит пользователь не является учителем
        return False


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ModelPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'size': self.page_size,
            'count': self.page.paginator.count,
            'results': data
        })

class AttendanceDateListView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        qs = None
        if(is_teacher(self.request.user)):
            teacher = get_object_or_404(Teacher, user_id=self.request.user)
            # Получить все объекты SubjectRealization, связанные с этим учителем
            subject_realizations = teacher.subjectrealization_set.all()
            # Получаем все объекты Attendance где данный учитель ведёт и заменяет
            teacher_attendance = Attendance.objects.filter(subject_realization_id__in=subject_realizations)
            teacher_replacement_attendance = Attendance.objects.filter(teacher_replacement=teacher)

            qs = teacher_attendance | teacher_replacement_attendance
        elif(is_student(self.request.user)):
            student = get_object_or_404(Student, user_id=self.request.user)
            student_group = get_object_or_404(Group, student__id=student.id)

            qs = Attendance.objects.filter(groups=student_group)
        else:
            qs = Attendance.objects.all()
            
        #FILTER
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        print(date_end)

        if date_start and date_end:
            qs = qs.filter(date__range = [date_start, date_end])
        return qs


class AttendanceListView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = AttendanceSerializer
    pagination_class = ModelPagination

    def get_queryset(self):
        qs = None
        if(is_teacher(self.request.user)):
            teacher = get_object_or_404(Teacher, user_id=self.request.user)
            # Получить все объекты SubjectRealization, связанные с этим учителем
            subject_realizations = teacher.subjectrealization_set.all()
            # Получаем все объекты Attendance где данный учитель ведёт и заменяет
            teacher_attendance = Attendance.objects.filter(subject_realization_id__in=subject_realizations)
            teacher_replacement_attendance = Attendance.objects.filter(teacher_replacement=teacher)

            qs = teacher_attendance | teacher_replacement_attendance
        elif(is_student(self.request.user)):
            student = get_object_or_404(Student, user_id=self.request.user)
            student_group = get_object_or_404(Group, student__id=student.id)

            qs = Attendance.objects.filter(groups=student_group)
        else:
            qs = Attendance.objects.all()
            
        #SORT
        field_to_sort_by = self.request.GET.get('sort_field', 'date')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if field_to_sort_by and field_to_sort_by.strip():
            if field_to_sort_by == 'type':
                field_to_sort_by = "subject_realization_id__type"
            elif field_to_sort_by == 'subject':
                field_to_sort_by = "subject_realization_id__subject_id__name"
            elif field_to_sort_by == 'faculty':
                field_to_sort_by = "groups__course_id__faculty_id__name"
            if sort_order == 'descend':
                qs = qs.order_by(F(field_to_sort_by).desc(),"date","time_start")
            else:
                qs = qs.order_by(F(field_to_sort_by).asc(),"date","time_start")

        #FILTER
        subject = self.request.GET.get('subject')
        last_name = self.request.GET.get('last_name')
        first_name = self.request.GET.get('first_name')
        middle_name = self.request.GET.get('middle_name')

        date_start = self.request.GET.get('date[start]')
        date_end = self.request.GET.get('date[end]')

        time_start_start = self.request.GET.get('time_start[start]')
        time_start_end = self.request.GET.get('time_start[end]')

        group = self.request.GET.get('group')

        type = self.request.GET.get('type')

        teacher_replacement = self.request.GET.get('teacher_replacement')

        faculty = self.request.GET.get('faculty')

        isComplete = self.request.GET.get('isComplete')

        if faculty:
            qs = qs.filter(groups__course_id__faculty_id__name__icontains = faculty)
        if isComplete == "true":
            qs = qs.filter(isComplete = True)
        if isComplete == "false":
            qs = qs.filter(isComplete = False)
        if subject:
            qs = qs.filter(subject_realization_id__subject_id__name__icontains = subject)
        if last_name:
            if teacher_replacement == "true":
                qs = qs.filter(
                    Q(subject_realization_id__teacher_id__user_id__last_name__icontains=last_name) |
                    Q(teacher_replacement__user_id__last_name__icontains=last_name)
                )
            else:
                qs =  qs.filter(subject_realization_id__teacher_id__user_id__last_name__icontains=last_name)
        if first_name:
            if teacher_replacement == "true":
                qs = qs.filter(
                    Q(subject_realization_id__teacher_id__user_id__first_name__icontains=first_name) |
                    Q(teacher_replacement__user_id__first_name__icontains=first_name)
                )
            else:
                qs = qs.filter(subject_realization_id__teacher_id__user_id__first_name__icontains =  first_name)
        if middle_name:
            if teacher_replacement == "true":
                qs = qs.filter(
                    Q(subject_realization_id__teacher_id__user_id__middle_name__icontains=middle_name) |
                    Q(teacher_replacement__user_id__middle_name__icontains=middle_name)
                )
            else:
                qs = qs.filter(subject_realization_id__teacher_id__user_id__middle_name__icontains =  middle_name)
        if date_start and date_end:
            qs = qs.filter(date__range = [date_start, date_end])
        if time_start_start and time_start_end:
            qs = qs.filter(time_start__range = [time_start_start, time_start_end])
        if group:
            qs = qs.filter(subject_realization_id__groups__name__icontains = group)
        if type:
            qs = qs.filter(subject_realization_id__type__icontains = type)

        return qs

class AttendanceDetailView(generics.RetrieveAPIView):
    queryset = Attendance.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class = AttendanceSerializer

class AttendanceReportGroupDetailView(generics.ListAPIView):
     permission_classes=[IsAuthenticated]
     serializer_class = AttendanceReportGroupSerializer
     pagination_class = None
     def get_queryset(self):
        qs = Student.objects.filter(group_id=self.kwargs['group_pk'])
        qs = qs.order_by('user_id__last_name', 'user_id__first_name', 'user_id__middle_name')
        return qs
     def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'attendance_id': self.kwargs['pk']})
        return context

class AttendanceReportGroupCompleteApiView(APIView):
    permission_classes=[IsAuthenticated, IsTeacher]
    def post(self, request, pk):
        try:
            attendance = Attendance.objects.get(pk=pk)
            attendance_groups = attendance.groups.all()

            for group in attendance_groups:
                # Получаем всех студентов, присутствовавших на занятии в этой группе
                students_attended = AttendanceReport.objects.filter(attendance_id=pk, student_id__group_id=group).values_list('student_id', flat=True).distinct()

                # Проверяем, что для каждого студента есть соответствующая запись в AttendanceReport
                if len(students_attended) == group.student_set.count():
                    # Получаем все записи AttendanceReport для этой группы
                    attendance_reports = AttendanceReport.objects.filter(attendance_id=pk)
                    # Проверяем, все ли записи имеют непустой статус
                    if not all(report.status != "" for report in attendance_reports):
                        return Response({"message": "Отмечены не все студенты"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Отмечены не все студенты"}, status=status.HTTP_400_BAD_REQUEST)
            attendance.isComplete = True
            attendance.save()
            return Response({"message": "Отмечено как подтвержденное"}, status=status.HTTP_200_OK)

        except Attendance.DoesNotExist:
            return Response({"message": "Занятие не найдено"}, status=status.HTTP_404_NOT_FOUND)


class AttendanceReportCreateEditAPIView(APIView):
    permission_classes=[IsAuthenticated, IsTeacherOrHeadman]
    def post(self, request):
        serializer = AttendanceReportSerializer(data=request.data)
        if serializer.is_valid():
            student_id = serializer.validated_data['student_id']
            attendance_id = serializer.validated_data['attendance_id']
            # Проверяем, существует ли уже отчет для студента и мероприятия
            try:
                attendance_report = AttendanceReport.objects.get(student_id=student_id, attendance_id=attendance_id)
                serializer = AttendanceReportSerializer(attendance_report, data=request.data)
                print(serializer)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except AttendanceReport.DoesNotExist:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AttendanceReportsCreateEditAPIView(APIView):
    permission_classes=[IsAuthenticated, IsTeacherOrHeadman]
    def post(self, request):
        for student_id in request.data["students_id"]:
            data = {'student_id': student_id, 'attendance_id': request.data["attendance_id"], 'status': request.data['status']}
            serializer = AttendanceReportSerializer(data=data)
            if serializer.is_valid():
                student_id = serializer.validated_data['student_id']
                attendance_id = serializer.validated_data['attendance_id']
                try:
                    attendance_report = AttendanceReport.objects.get(student_id=student_id, attendance_id=attendance_id)
                    serializer = AttendanceReportSerializer(attendance_report, data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except AttendanceReport.DoesNotExist:
                    serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubjectRealizationListView(generics.ListAPIView):
    serializer_class = SubjectRealizationSerializer
    permission_classes=[IsAuthenticated]
    pagination_class = ModelPagination
    def get_queryset(self):
        if(is_teacher(self.request.user)):
            teacher = get_object_or_404(Teacher, user_id=self.request.user.id)
            subject_realizations  = SubjectRealization.objects.filter(teacher_id=teacher.id)
            qs = Subject.objects.filter(subjectrealization__in=subject_realizations).distinct()
        if(is_student(self.request.user)):
            student = get_object_or_404(Student, user_id=self.request.user.id)
            attendances = Attendance.objects.filter(groups=student.group_id)
            subjects = SubjectRealization.objects.filter(attendance__in=attendances).values_list('subject_id', flat=True).distinct()
            qs = Subject.objects.filter(id__in=subjects)
        #SORT
        field_to_sort_by = self.request.GET.get('sort_field')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if field_to_sort_by and field_to_sort_by.strip():
            if field_to_sort_by == 'subject':
                field_to_sort_by = "name"
            if sort_order == 'descend':
                qs = qs.order_by(F(field_to_sort_by).desc())
            else:
                qs = qs.order_by(F(field_to_sort_by).asc())
        #FILTER
        subject = self.request.GET.get('subject')
        if subject:
            qs = qs.filter(name__icontains = subject)

        return qs
     
        
class GroupListApiView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = GroupSerializer
    pagination_class = ModelPagination
    def get_queryset(self):
        # subject_realization = get_object_or_404(SubjectRealization, id=self.kwargs['pk'])
        if 'pk' in self.kwargs and self.kwargs['pk']:
            subject = Subject.objects.get(pk=self.kwargs['pk'])
            subject_realizations = subject.subjectrealization_set.all()
            qs = Group.objects.filter(attendance__subject_realization_id__in=subject_realizations).distinct()
        else:
            qs = Group.objects.all().distinct()


        #SORT
        field_to_sort_by = self.request.GET.get('sort_field')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if field_to_sort_by and field_to_sort_by.strip():
            if field_to_sort_by == 'faculty':
                field_to_sort_by = "course_id__faculty_id__name"
            elif field_to_sort_by == 'course':
                field_to_sort_by = "course_id__name"
            if sort_order == 'descend':
                qs = qs.order_by(F(field_to_sort_by).desc())
            else:
                qs = qs.order_by(F(field_to_sort_by).asc())

        #FILTER
        name = self.request.GET.get('name')
        faculty = self.request.GET.get('faculty')
        course = self.request.GET.get('course')
        if name:
            qs = qs.filter(name__icontains = name)
        if faculty:
            qs = qs.filter(course_id__faculty_id__name__icontains = faculty)
        if course:
            qs = qs.filter(course_id__name__icontains = course)

        return qs
    
class SubjectJournalApiView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, subject_id, group_id):
        subject_realizations = SubjectRealization.objects.filter(subject_id=subject_id)
        students = Student.objects.filter(group_id=group_id).order_by('user_id__last_name', 'user_id__first_name', 'user_id__middle_name')
        attendances = Attendance.objects.filter(subject_realization_id__in=subject_realizations, groups__id=group_id).order_by('date','time_start','time_end')
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendances.values_list('id', flat=True))

        data = []
        for student in students:
            student_row = []
            for attendance in attendances:
                report = attendance_reports.filter(attendance_id=attendance.id, student_id=student.id).first()
                if report:
                    student_row.append({'id': attendance.id, 'report_id': report.id, 'status': report.get_status_display()})
                else:
                    student_row.append({'id': attendance.id, 'report_id': '', 'status': ''})
            data.append({'student': StudentSerializer(student).data, 'report_row': student_row})

        return Response({'students': data, 'attendances': AttendanceSimpleSerializer(attendances, many=True).data, 'data': data})
    



def get_month_day_column_headers(year, month):
    num_days = calendar.monthrange(year, month)[1]
    return [str(day) for day in range(1, num_days + 1)]

def generate_daily_attendance_data(year, month,attendances):
    num_days = calendar.monthrange(year, month)[1]
    data = {}
    for day in range(1, num_days + 1):
        date = timezone.datetime(year, month, day)
        date_str = date.strftime('%Y-%m-%d')
        attendance_data = {}
        # Получаем все посещения для текущего дня
        new_attendances = attendances.filter(date=date_str)
      
        data[date_str] =   AttendanceSimpleSerializer(new_attendances, many=True).data
    return data

class JournalApiView(APIView):
    # permission_classes=[IsAuthenticated]
    def get(self, request, group_id):
        year = request.GET.get('year')
        month = request.GET.get('month')
        print(year,month)
        if year and month and group_id:
            students = Student.objects.filter(group_id=group_id)
            start_date = datetime.datetime(int(year), int(month), 1)
            if int(month) == 12:
                end_date = datetime.datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime.datetime(int(year), int(month) + 1, 1)
            # Фильтруем объекты Attendance по диапазону дат
            attendances = Attendance.objects.filter(groups__id=group_id, date__gte=start_date, date__lt=end_date).order_by('date', 'time_start', 'time_end')
            attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendances.values_list('id', flat=True))
            monthly_attendance_data = generate_daily_attendance_data(int(year), int(month),attendances)

            data = []
            for student in students:
                student_row = []
                for attendance in attendances:
                    report = attendance_reports.filter(attendance_id=attendance.id, student_id=student.id).first()
                    if report:
                        student_row.append({'id': attendance.id, 'report_id': report.id, 'status': report.get_status_display()})
                    else:
                        student_row.append({'id': attendance.id, 'report_id': '', 'status': ''})
                data.append({'student': StudentSerializer(student).data, 'report_row': student_row})




            return Response( {"attendances": monthly_attendance_data,"students":data})
        








        else:
            return Response({'message': 'Year, month, and id_group parameters are required.'})

class StudentAttendanceReportList(APIView):
    def get(self,request, user_id):
        student_id = user_id
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print(start_date)
        # Проверяем, что start_date и end_date переданы
        if start_date and end_date:
            attendance_reports = AttendanceReport.objects.filter(student_id=student_id, attendance_id__date__range=(start_date, end_date))
            print(attendance_reports)
        else:
            attendance_reports = AttendanceReport.objects.filter(student_id=student_id)
        student = Student.objects.get(id=student_id)
        attendances = Attendance.objects.filter(groups__student=student)
        subjects = Subject.objects.filter(subjectrealization__attendance__in=attendances).distinct()
        return Response({
            "attendanceReportData": AttendanceReportSerializer(attendance_reports,many=True).data, 
            "subjects": SubjectSerializer(subjects,many=True).data,
            "student": StudentSerializer(student).data
            })

class TeacherAttendanceReportList(APIView):
    def get(self,request, user_id):
        teacher_id = user_id
        teacher = Teacher.objects.get(id=teacher_id)
        return Response({
            "teacher": TeacherSerializer(teacher).data
            })
 
class StudentsList(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = StudentSerializer
    pagination_class = ModelPagination
    def get_queryset(self):
        
        qs = Student.objects.all()

        #SORT
        field_to_sort_by = self.request.GET.get('sort_field')
        sort_order = self.request.GET.get('sort_order', 'asc')
       
        if field_to_sort_by and field_to_sort_by.strip():
            if field_to_sort_by == 'first_name':
                field_to_sort_by = "user_id__first_name"
            elif field_to_sort_by == 'middle_name':
                field_to_sort_by = "user_id__middle_name"
            elif field_to_sort_by == 'last_name':
                field_to_sort_by = "user_id__last_name"
            if sort_order == 'descend':
                qs = qs.order_by(F(field_to_sort_by).desc())
            else:
                qs = qs.order_by(F(field_to_sort_by).asc())
        #FILTER
        isHeadman = self.request.GET.get('isHeadman')
        group = self.request.GET.get('group')
        first_name = self.request.GET.get('first_name')
        middle_name = self.request.GET.get('middle_name')
        last_name = self.request.GET.get('last_name')
        if group:
            qs = qs.filter(group_id__name__icontains=group)
        if first_name:
            qs = qs.filter(user_id__first_name__icontains=first_name)
        if middle_name:
            qs = qs.filter(user_id__middle_name__icontains=middle_name)
        if last_name:
                qs = qs.filter(user_id__last_name__icontains=last_name)

        
        return qs

class TeachersList(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = TeacherSerializer
    pagination_class = ModelPagination
    def get_queryset(self):
        
        qs = Teacher.objects.all()

        #SORT
        field_to_sort_by = self.request.GET.get('sort_field')
        sort_order = self.request.GET.get('sort_order', 'asc')
       
        if field_to_sort_by and field_to_sort_by.strip():
            if field_to_sort_by == 'first_name':
                field_to_sort_by = "user_id__first_name"
            elif field_to_sort_by == 'middle_name':
                field_to_sort_by = "user_id__middle_name"
            elif field_to_sort_by == 'last_name':
                field_to_sort_by = "user_id__last_name"
            if sort_order == 'descend':
                qs = qs.order_by(F(field_to_sort_by).desc())
            else:
                qs = qs.order_by(F(field_to_sort_by).asc())
        #FILTER
        group = self.request.GET.get('group')
        first_name = self.request.GET.get('first_name')
        middle_name = self.request.GET.get('middle_name')
        last_name = self.request.GET.get('last_name')
        job_title = self.request.GET.get('job_title')
        scientific_title = self.request.GET.get('scientific_title')
        if group:
            qs = qs.filter(group_id__name__icontains=group)
        if first_name:
            qs = qs.filter(user_id__first_name__icontains=first_name)
        if middle_name:
            qs = qs.filter(user_id__middle_name__icontains=middle_name)
        if last_name:
            qs = qs.filter(user_id__last_name__icontains=last_name)
        if job_title:
            qs = qs.filter(job_title__icontains=job_title)
        if scientific_title:
            qs = qs.filter(scientific_title__icontains=scientific_title)

        
        return qs

class GroupDetail(APIView):
    def get(self,request, group_id):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        students = Student.objects.filter(group_id=group_id)
        # Проверяем, что start_date и end_date переданы
        all_attendance_reports = []
        for student in students:
            if start_date and end_date:
                attendance_reports = AttendanceReport.objects.filter(student_id=student.id, attendance_id__date__range=(start_date, end_date))
            else:
                attendance_reports = AttendanceReport.objects.filter(student_id=student.id)
            all_attendance_reports.extend(attendance_reports)
        print(students)
            
        group = Group.objects.get(id=group_id)
        attendances = Attendance.objects.filter(groups__id=group_id)
        subjects = Subject.objects.filter(subjectrealization__attendance__in=attendances).distinct()
        return Response({
            "attendanceReportData": AttendanceReportSerializer(all_attendance_reports,many=True).data, 
            "subjects": SubjectSerializer(subjects,many=True).data,
            "group": GroupSerializer(group).data,
            "students": StudentSerializer(students, many=True).data
            })
    pass
    # def get(self,request, group_id):
    #     start_date = request.GET.get('start_date')
    #     end_date = request.GET.get('end_date')
    #     print(start_date)
    #     # Проверяем, что start_date и end_date переданы
    #     if start_date and end_date:
    #         attendance_reports = AttendanceReport.objects.filter(student_id=student_id, attendance_id__date__range=(start_date, end_date))
    #         print(attendance_reports)
    #     else:
    #         attendance_reports = AttendanceReport.objects.filter(student_id=student_id)
    #     group = Group.objects.get(id=group_id)
    #     attendances = Attendance.objects.filter(groups__student=student)
    #     subjects = Subject.objects.filter(subjectrealization__attendance__in=attendances).distinct()
    #     return Response({
    #         "attendanceReportData": AttendanceReportSerializer(attendance_reports,many=True).data, 
    #         "subjects": SubjectSerializer(subjects,many=True).data,
    #         "group": GroupSerializer(group).data
    #         })



class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializerCRUD

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializerCRUD

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializerCRUD

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerCRUD

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializerCRUD

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializerCRUD

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializerCRUD

class SubjectRealizationViewSet(viewsets.ModelViewSet):
    queryset = SubjectRealization.objects.all()
    serializer_class = SubjectRealizationSerializerCRUD

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializerCRUD

class AttendanceReportViewSet(viewsets.ModelViewSet):
    queryset = AttendanceReport.objects.all()
    serializer_class = AttendanceReportSerializerCRUD