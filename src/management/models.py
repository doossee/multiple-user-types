from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"

    base_role = Role.ADMIN

    role = models.CharField(max_length=9, choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super(User, self).save(*args, **kwargs)


class StudentManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.STUDENT)


class Student(User):

    base_role = User.Role.STUDENT

    class Meta:
        proxy = True

    student = StudentManager()

    def welcome(self):
        return "Only for students"
   

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.PositiveIntegerField(null=True, blank=True)

    
@receiver(post_save, sender=Student)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "STUDENT":
        StudentProfile.objects.create(user=instance)


class TeacherManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.TEACHER)


class Teacher(User):

    base_role = User.Role.TEACHER

    class Meta:
        proxy = True

    teachers = TeacherManager()

    def welcome(self):
        return "Only for teachers"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.PositiveIntegerField(null=True, blank=True)


@receiver(post_save, sender=Student)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "TEACHER":
        TeacherProfile.objects.create(user=instance)
