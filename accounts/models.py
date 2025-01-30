from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    USER_TYPE = (('1', "Admin"), ('2', "Voter"))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stud_no = models.CharField(max_length=10, unique=True)
    user_type = models.CharField(default='2', choices=USER_TYPE, max_length=1)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.stud_no}"

    @classmethod
    def create_admin_profile(cls, user):
        profile = cls.objects.get(user=user)
        profile.user_type = '1'  # Set as Admin
        profile.is_approved = True  # Automatically approve admin users
        profile.save()
        return profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        if instance.is_superuser:
            profile.user_type = '1'  # Set as Admin
            profile.is_approved = True
            profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class ApprovedStudent(models.Model):
    student_number = models.CharField(max_length=10, unique=True)  # Student number field

    def __str__(self):
        return self.student_number