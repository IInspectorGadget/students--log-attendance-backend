# Generated by Django 5.0.2 on 2024-03-06 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_attendancereport_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='attendance_date',
        ),
        migrations.AddField(
            model_name='attendance',
            name='date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='time_end',
            field=models.TimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='time_start',
            field=models.TimeField(auto_now=True),
        ),
    ]
