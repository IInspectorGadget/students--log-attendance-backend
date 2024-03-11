# Generated by Django 5.0.2 on 2024-03-07 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_subjectrealization_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='course_id',
        ),
        migrations.RemoveField(
            model_name='subjectrealization',
            name='groups',
        ),
        migrations.AddField(
            model_name='attendance',
            name='groups',
            field=models.ManyToManyField(to='api.group'),
        ),
    ]
