from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    user_type_data=[("1","Administrator"),("2","Teacher"),("3","Student")]
    user_type=models.CharField(default=1,choices=user_type_data,max_length=20)
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    middle_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=12, blank=True)

    def __str__(self):
        return ' '.join([self.get_user_type_display(), self.username, self.first_name, self.last_name, self.middle_name])

class Faculty(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Course(models.Model):
    id=models.AutoField(primary_key=True)
    faculty_id = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING)
    name=models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Teacher(models.Model):
    id = models.AutoField(primary_key=True, db_index = True)
    user_id = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    phone = models.CharField(max_length=12)

    def __str__(self):
        return str(self.user_id)

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Student(models.Model):
    id=models.AutoField(primary_key=True, db_index = True)
    user_id=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    group_id=models.ForeignKey(Group,on_delete=models.DO_NOTHING, default=1)
    isHeadman = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user_id)

class Subject(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SubjectRealization(models.Model):
    id=models.AutoField(primary_key=True)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    type_data=[("лекция","лекция"),("практика","практика")]
    type=models.CharField(default="лекция",choices=type_data,max_length=20)

    def __str__(self):
        return ' '.join([str(self.subject_id)])
    
class Attendance(models.Model):
    id=models.AutoField(primary_key=True)
    subject_realization_id = models.ForeignKey(SubjectRealization, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date=models.DateField()
    time_start=models.TimeField()
    time_end=models.TimeField()
    groups = models.ManyToManyField(Group)
    teacher_replacement = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, blank=True, null = True)
    isComplete = models.BooleanField(default=False)
    def __str__(self):
        return str(int(self.id)) + ' '.join([str(self.teacher_replacement), str(self.date)])

class AttendanceReport(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Student,on_delete=models.DO_NOTHING)
    attendance_id=models.ForeignKey(Attendance,on_delete=models.CASCADE)
    last_edit_time = models.TimeField(auto_now=True)
    status_data=[("1","+"),("2","Н"), ("3",'П'), ("4",'Б')]
    status=models.CharField(default=1,choices=status_data,max_length=1)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == "2":  # если тип пользователя - учитель
            Teacher.objects.create(user_id=instance)
        elif instance.user_type == "3":  # если тип пользователя - студент
            Student.objects.create(user_id=instance)