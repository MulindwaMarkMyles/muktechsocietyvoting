from django.shortcuts import render, redirect, reverse
from accounts.views import account_login
from .models import Position, Candidate, Voter, Votes, VotingControl
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import requests
import json
# Create your views here.

def index(request):
    context = {}
    return render(request, "voting/index.html", context)

def generate_ballot(display_controls=False):
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1
    # return None
    for position in positions:
        name = position.name
        position_name = slugify(name)
        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:
            if position.max_vote > 1:
                instruction = "You may select up to " + \
                    str(position.max_vote) + " candidates"
                input_box = '<input type="checkbox" value="'+str(candidate.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '">'
            else:
                instruction = "Select only one candidate"
                input_box = '<input value="'+str(candidate.id)+'" type="radio" class="flat-red ' + \
                    position_name+'" name="'+position_name+'">'
            image = "/media/" + str(candidate.photo)
            candidates_data = candidates_data + '<li>' + input_box + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="'+candidate.fullname+'" data-bio="'+candidate.bio+'"><i class="fa fa-search"></i> Platform</button><img src="' + \
                image+'" height="100px" width="100px" class="clist"><span class="cname clist">' + \
                candidate.fullname+'</span></li>'
        up = ''
        if position.priority == 1:
            up = 'disabled'
        down = ''
        if position.priority == positions.count():
            down = 'disabled'
        output = output + f"""<div class="row">	<div class="col-xs-12"><div class="box box-solid" id="{position.id}">
             <div class="box-header with-border">
            <h3 class="box-title"><b>{name}</b></h3>"""

        if display_controls:
            output = output + f""" <div class="pull-right box-tools">
        <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
        <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
        </div>"""

        output = output + f"""</div>
        <div class="box-body">
        <p>{instruction}
        <span class="pull-right">
        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
        </span>
        </p>
        <div id="candidate_list">
        <ul>
        {candidates_data}
        </ul>
        </div>
        </div>
        </div>
        </div>
        </div>
        """
        position.priority = num
        position.save()
        num = num + 1
        candidates_data = ''
    return output


def fetch_ballot(request):
    output = generate_ballot(display_controls=True)
    return JsonResponse(output, safe=True)

def dashboard(request):
    user = request.user
    
    # Clear any redirect tracking that might have been set
    if 'redirect_count' in request.session:
        del request.session['redirect_count']
        
    try:
        if not get_voting_status():
            messages.error(request, "Voting is currently disabled by administrators")
            return redirect(reverse('account_login'))
        
        print(user)
        print("trying")
        if not hasattr(user, 'voter'):
            messages.error(request, "Voter profile not found. Please contact support.")
            return redirect(reverse('account_login'))
            
        voter = user.voter  # Access the related voter object
        if voter.voted:
            print("voted")
            return render(request, "voting/voter/result.html", {'my_votes': Votes.objects.filter(voter=voter)})
        else:
            # Set a flag to track redirect
            request.session['from_dashboard'] = True
            return redirect(reverse('show_ballot'))
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect(reverse('account_login'))

def verify(request):
    context = {
        'page_title': 'OTP Verification'
    }
    return render(request, "voting/voter/verify.html", context)

def show_ballot(request):
    # Check for redirect loop
    redirect_count = request.session.get('redirect_count', 0)
    if redirect_count > 2:  # If redirected more than twice, break the loop
        messages.error(request, "Too many redirects detected. Please contact support.")
        request.session.pop('redirect_count', None)
        return redirect(reverse('account_login'))
    
    # Increment redirect counter
    request.session['redirect_count'] = redirect_count + 1
    
    # Check if voting is enabled
    if not get_voting_status():
        messages.error(request, "Voting is currently disabled by administrators")
        return redirect(reverse('account_login'))
    
    # Safely check if user is authenticated and has a voter profile
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to access the ballot.")
        return redirect(reverse('account_login'))
    
    try:
        voter = request.user.voter
        if voter.voted:
            messages.error(request, "You have voted already")
            return redirect(reverse('voterDashboard'))
        
        ballot = generate_ballot(display_controls=False)
        context = {
            'ballot': ballot
        }
        # Clear redirect counter on successful render
        if 'redirect_count' in request.session:
            del request.session['redirect_count']
        return render(request, "voting/voter/ballot.html", context)
    except Exception as e:
        messages.error(request, f"Error retrieving ballot: {str(e)}")
        return redirect(reverse('account_login'))

def preview_vote(request):
    if request.method != 'POST':
        error = True
        response = "Please browse the system properly"
    else:
        output = ""
        form = dict(request.POST)
        # We don't need to loop over CSRF token
        form.pop('csrfmiddlewaretoken', None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:
            max_vote = position.max_vote
            pos = slugify(position.name)
            pos_id = position.id
            if position.max_vote > 1:
                this_key = pos + "[]"
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                if len(form_position) > max_vote:
                    error = True
                    response = "You can only choose " + \
                        str(max_vote) + " candidates for " + position.name
                else:
                    # for key, value in form.items():
                    start_tag = f"""
                       <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'>
                                <ul style='list-style-type:none; margin-left:-40px'>
                                
                    
                    """
                    end_tag = "</ul></span></div><hr/>"
                    data = ""
                    for form_candidate_id in form_position:
                        try:
                            candidate = Candidate.objects.get(
                                id=form_candidate_id, position=position)
                            data += f"""
		                      	<li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                            """
                        except:
                            error = True
                            response = "Please, browse the system properly"
                    output += start_tag + data + end_tag
            else:
                this_key = pos
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                # Max Vote == 1
                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position)
                    output += f"""
                            <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
		                    </div>
                      <hr/>
                    """
                except Exception as e:
                    error = True
                    response = "Please, browse the system properly"
    context = {
        'error': error,
        'list': output
    }
    return JsonResponse(context, safe=False)

def submit_ballot(request):
    # Check if voting is enabled
    if not get_voting_status():
        messages.error(request, "Voting is currently disabled by administrators")
        return redirect(reverse('account_login'))
        
    if request.method != 'POST':
        messages.error(request, "Please, browse the system properly")
        return redirect(reverse('show_ballot'))

    # Verify if the voter has voted or not
    voter = request.user.voter
    if voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse('voterDashboard'))

    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)  # Pop CSRF Token
    form.pop('submit_vote', None)  # Pop Submit Button

    # Ensure at least one vote is selected
    if len(form.keys()) < 1:
        messages.error(request, "Please select at least one candidate")
        return redirect(reverse('show_ballot'))
    positions = Position.objects.all()
    form_count = 0
    for position in positions:
        max_vote = position.max_vote
        pos = slugify(position.name)
        pos_id = position.id
        if position.max_vote > 1:
            this_key = pos + "[]"
            form_position = form.get(this_key)
            if form_position is None:
                continue
            if len(form_position) > max_vote:
                messages.error(request, "You can only choose " +
                               str(max_vote) + " candidates for " + position.name)
                return redirect(reverse('show_ballot'))
            else:
                for form_candidate_id in form_position:
                    form_count += 1
                    try:
                        candidate = Candidate.objects.get(
                            id=form_candidate_id, position=position)
                        vote = Votes()
                        vote.candidate = candidate
                        vote.voter = voter
                        vote.position = position
                        vote.save()
                    except Exception as e:
                        messages.error(
                            request, "Please, browse the system properly " + str(e))
                        return redirect(reverse('show_ballot'))
        else:
            this_key = pos
            form_position = form.get(this_key)
            if form_position is None:
                continue
            # Max Vote == 1
            form_count += 1
            try:
                form_position = form_position[0]
                candidate = Candidate.objects.get(
                    position=position, id=form_position)
                vote = Votes()
                vote.candidate = candidate
                vote.voter = voter
                vote.position = position
                vote.save()
            except Exception as e:
                messages.error(
                    request, "Please, browse the system properly " + str(e))
                return redirect(reverse('show_ballot'))
    # Count total number of records inserted
    # Check it viz-a-viz form_count
    inserted_votes = Votes.objects.filter(voter=voter)
    if (inserted_votes.count() != form_count):
        # Delete
        inserted_votes.delete()
        messages.error(request, "Please try voting again!")
        return redirect(reverse('show_ballot'))
    else:
        # Update Voter profile to voted
        voter.voted = True
        voter.save()
        messages.success(request, "Thanks for voting")
        return redirect(reverse('voterDashboard'))

def get_voting_status():
    """Helper function to check if voting is enabled"""
    voting_control = VotingControl.objects.first()
    if not voting_control:
        return False
    return voting_control.is_active

def vote(request):
    if not get_voting_status():
        messages.error(request, "Voting is currently disabled")
        return redirect('home')  # Or wherever appropriate
    
    # ...rest of your voting view code...
