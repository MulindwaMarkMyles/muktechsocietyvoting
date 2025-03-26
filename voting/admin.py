from django.contrib import admin
from django.utils import timezone
from .models import Voter, Position, Candidate, Votes, VotingControl
from django.http import HttpResponseRedirect
from django.urls import path

class VotingControlAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'started_at', 'ended_at')
    search_fields = ('title',)
    list_filter = ('is_active',)
    readonly_fields = ('started_at', 'ended_at', 'created_by')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle_voting/',
                 self.admin_site.admin_view(self.toggle_voting),
                 name='toggle-voting'),
        ]
        return custom_urls + urls
    
    def toggle_voting(self, request):
        # Get the first voting control object or create one if none exists
        voting_control = VotingControl.objects.first()
        if not voting_control:
            voting_control = VotingControl.objects.create(created_by=request.user)
        
        # Toggle the status and update timestamps
        if voting_control.is_active:
            voting_control.is_active = False
            voting_control.ended_at = timezone.now()
        else:
            voting_control.is_active = True
            voting_control.started_at = timezone.now()
        
        voting_control.save()
        self.message_user(request, f"Voting is now {'enabled' if voting_control.is_active else 'disabled'}")
        return HttpResponseRedirect("../")
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        voting_control = VotingControl.objects.first()
        if voting_control:
            button_text = "Disable Voting" if voting_control.is_active else "Enable Voting"
            button_class = "default" if voting_control.is_active else "success"
        else:
            button_text = "Enable Voting"
            button_class = "success"
        
        extra_context.update({
            'button_text': button_text,
            'button_class': button_class,
        })
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Voter)
admin.site.register(Position)
admin.site.register(Candidate)
admin.site.register(Votes)
admin.site.register(VotingControl, VotingControlAdmin)
