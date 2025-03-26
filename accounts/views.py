from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from voting.models import VotingControl
from .models import ApprovedStudent, Profile
from .forms import CustomUserForm
from voting.forms import VoterForm

def account_login(request):
    voting_control = VotingControl.objects.first()
    if request.method == 'POST':
        stud_no = request.POST.get('stud_no', '').strip()
        password = request.POST.get('password', '')
        
        try:
            # Find the profile with matching student number
            profile = Profile.objects.get(stud_no=stud_no)
            user = authenticate(request=request, username=profile.user.username, password=password)
            
            if user is not None:
                login(request, user)
                if profile.user_type == '1':
                    return redirect(reverse("adminDashboard"))
                elif profile.user_type == '2':
                    voting_control = VotingControl.objects.first()
                    if voting_control.is_active:
                        return redirect(reverse("voterDashboard"))
                    else:
                        messages.error(request, "Voting is currently disabled")
                        return redirect(reverse("account_login"))
            else:
                messages.error(request, "Invalid credentials")
                return redirect(reverse('account_login'))
        except Profile.DoesNotExist:
            messages.error(request, "Student number not found")
            return redirect(reverse('account_login'))
        
    elif request.user.is_authenticated and voting_control.is_active and request.user.profile.user_type == '2':
        return redirect(reverse('voterDashboard'))
    
    elif request.user.is_authenticated and request.user.profile.user_type == '1':
        return redirect(reverse('adminDashboard'))
    return render(request, "voting/login.html")

def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm
    }

    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            student_number = userForm.cleaned_data.get('stud_no')

            # Check if student number is approved
            if not ApprovedStudent.objects.filter(student_number=student_number).exists():
                messages.error(request, "Your student number is not authorized to register.")
                return render(request, "voting/reg.html", context)

            # Check if student number is already registered
            if Profile.objects.filter(stud_no=student_number).exists():
                messages.error(request, "This student number is already registered.")
                return render(request, "voting/reg.html", context)

            # Create User instance
            user = User.objects.create_user(
                username=student_number,  # Using student number as username
                email=userForm.cleaned_data.get('email'),
                password=userForm.cleaned_data.get('password'),
                first_name=userForm.cleaned_data.get('first_name'),
                last_name=userForm.cleaned_data.get('last_name')
            )

            # Update Profile
            profile = user.profile
            profile.stud_no = student_number
            profile.user_type = '2'  # Default to voter
            profile.save()

            # Create Voter
            voter = voterForm.save(commit=False)
            voter.admin = user
            voter.save()

            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")
            print("User Form Errors:", userForm.errors)
            print("Voter Form Errors:", voterForm.errors)

    return render(request, "voting/reg.html", context)

def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(
            request, "Sorry, you need to be logged in to perform this action")

    return redirect("account_login")
