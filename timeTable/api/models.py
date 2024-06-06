from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    user_type_data=[("1","Administrator"),("2","Teacher"),("3","Student")]
    user_type=models.CharField(default=1,choices=user_type_data,max_length=20, verbose_name="Тип пользователя")
    email = models.EmailField(blank=True, verbose_name="Email")
    first_name = models.CharField(max_length=30, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    phone = models.CharField(max_length=12, blank=True, verbose_name="Телефон")

    def __str__(self):
        return ' '.join([self.last_name,self.first_name,self.middle_name])

class Faculty(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255, verbose_name="Факультет")
    def __str__(self):
        return str(self.name)
    class Meta:
        verbose_name_plural = "Факультеты"


class Course(models.Model):
    id=models.AutoField(primary_key=True)
    faculty_id = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING, verbose_name="Факультет")
    name=models.CharField(max_length=255, verbose_name="Курс")

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name_plural = "Направления"

    
class Teacher(models.Model):
    id = models.AutoField(primary_key=True, db_index = True)
    user_id = models.OneToOneField(CustomUser,on_delete=models.CASCADE, verbose_name="Пользователь")
    job_title = models.CharField(max_length=255, verbose_name="Должность", blank=True)
    scientific_title = models.CharField(max_length=255, verbose_name="Звание", blank=True)
    def __str__(self):
        return ' '.join([self.user_id.last_name,self.user_id.first_name,self.user_id.middle_name])

    class Meta:
        verbose_name_plural = "Учителя"


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255,verbose_name="Группа")
    year = models.CharField(max_length=4, verbose_name="Год создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Группы"


class Student(models.Model):
    id=models.AutoField(primary_key=True, db_index = True)
    user_id=models.OneToOneField(CustomUser,on_delete=models.CASCADE,verbose_name="Пользователь")
    group_id=models.ForeignKey(Group,on_delete=models.DO_NOTHING, default=1)
    isHeadman = models.BooleanField(default=False,verbose_name="Староста?")
    zk = models.CharField(max_length=255,verbose_name="Номер зачетной кнжики")
    
    def __str__(self):
        return ' '.join([self.user_id.last_name,self.user_id.first_name,self.user_id.middle_name])
    
    class Meta:
        verbose_name_plural = "Студенты"


class Subject(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255,verbose_name="Предмет")
    def __str__(self):
        return str(self.name)
    class Meta:
        verbose_name_plural = "Предмет"

class SubjectRealization(models.Model):
    id=models.AutoField(primary_key=True)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING,verbose_name="Преподаватель")
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет")
    type_data=[("лекция","лекция"),("практика","практика")]
    type=models.CharField(default="лекция",choices=type_data,max_length=20,verbose_name="Тип")
    def __str__(self):
        return ' | '.join([str(self.teacher_id),str(self.subject_id)])
    class Meta:
        verbose_name_plural = "Реализация предмета"

    
class Attendance(models.Model):
    id=models.AutoField(primary_key=True)
    subject_realization_id = models.ForeignKey(SubjectRealization, on_delete=models.CASCADE, verbose_name='Реализация предмета')
    location = models.CharField(max_length=255,verbose_name="Место проведения")
    date=models.DateField(verbose_name="Дата")
    time_start=models.TimeField(verbose_name="Время начала")
    time_end=models.TimeField(verbose_name="Время конца")
    groups = models.ManyToManyField(Group, verbose_name="Группы")
    teacher_replacement = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, blank=True, null = True, verbose_name="Замена")
    isComplete = models.BooleanField(default=False,verbose_name="Подтвержден?")

    def __str__(self):
        return ' | '.join([str(self.subject_realization_id),str(self.date),str(self.time_start)])
    
    class Meta:
        verbose_name_plural = "Занятия"

  

class AttendanceReport(models.Model):
    id=models.AutoField(primary_key=True)
    student_id=models.ForeignKey(Student,on_delete=models.DO_NOTHING, verbose_name="Студент")
    attendance_id=models.ForeignKey(Attendance,on_delete=models.CASCADE, verbose_name="Занятие")
    last_edit_time = models.TimeField(auto_now=True,verbose_name="Последние изменение")
    status_data=[("1","+"),("2","Н"), ("3",'П'), ("4",'Б')]
    status=models.CharField(default=1,choices=status_data,max_length=1,verbose_name="Статус")

    def __str__(self):
        return ' | '.join([str(self.student_id),str(self.attendance_id),self.get_status_display()])

    class Meta:
        verbose_name_plural = "Отметки посещаемости"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == "2":  # если тип пользователя - учитель
            Teacher.objects.create(user_id=instance)
        elif instance.user_type == "3":  # если тип пользователя - студент
            Student.objects.create(user_id=instance)