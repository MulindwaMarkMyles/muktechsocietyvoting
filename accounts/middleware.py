from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages

class AccountCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Who is the current user ?
        if user.is_authenticated:
            if user.profile.user_type == '1':  # Admin
                if modulename == 'voting.views':
                    if request.path != reverse('fetch_ballot'):
                        messages.error(request, "You do not have access to this resource")
                        return redirect(reverse('adminDashboard'))
            elif user.profile.user_type == '2':  # Voter
                if modulename == 'administrator.views':
                    messages.error(request, "You do not have access to this resource")
                    return redirect(reverse('voterDashboard'))
            else:  # None of the aforementioned ? Please take the user to login page
                return redirect(reverse('account_login'))
        else:
            # If the path is login or has anything to do with authentication, pass
            if request.path in [reverse('account_login'), reverse('account_register')] or modulename == 'django.contrib.auth.views':
                pass
            # elif modulename in ['administrator.views', 'voting.views']:
            #     messages.error(request, "You need to be logged in to perform this operation")
            #     return render(request, "voting/login.html")
            # else:
            #     return render(request, "voting/login.html")