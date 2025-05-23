from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Voter(models.Model):
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, unique=True)  # Used for OTP
    # otp = models.CharField(max_length=10, null=True)
    verified = models.BooleanField(default=True)
    voted = models.BooleanField(default=False)
    # otp_sent = models.IntegerField(default=0)  # Control how many OTPs are sent

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    priority = models.IntegerField()

    def __str__(self):
        return self.name


class Candidate(models.Model):
    fullname = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)


class VotingControl(models.Model):
    """Controls whether voting is currently enabled or disabled system-wide"""
    is_active = models.BooleanField(default=False)
    title = models.CharField(max_length=50, default="Election")
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    class Meta:
        verbose_name = "Voting Control"
        verbose_name_plural = "Voting Controls"
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.title} - {status}"
