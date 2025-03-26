from django.forms import ModelForm, TextInput
from accounts.models import ApprovedStudent

class ApprovedStudentForm(ModelForm):
    class Meta:
        model = ApprovedStudent
        fields = ['student_number']
        widgets = {
            'student_number': TextInput(attrs={'class': 'form-control'})
        }