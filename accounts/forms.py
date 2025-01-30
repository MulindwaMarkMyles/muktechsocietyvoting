from django import forms
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.hashers import make_password

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

class CustomUserForm(FormSettings):
    password = forms.CharField(widget=forms.PasswordInput)
    stud_no = forms.CharField(max_length=10, label="Student Number")
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

