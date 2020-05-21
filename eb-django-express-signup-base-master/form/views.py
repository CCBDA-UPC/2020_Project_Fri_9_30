from django.http import HttpResponse
from django.shortcuts import render
from .models import Leads


def home(request):
    return render(request, 'index.html')


def signup(request):
    leads = Leads()
    status = leads.insert_lead(request.POST['MessageGroupId'], request.POST['email'],
                               request.POST['pop_size'],
                               request.POST['incubation_stage_duration'], request.POST['symptomatic_stage_duration'],
                               request.POST['min_recovery_duration'], request.POST['max_recovery_duration'],
                               request.POST['healthcare_capacity'],
                               request.POST['mortality_prob'],
                               request.POST['amt_has_app'], request.POST['efficiency'])

    # request.POST['mean_number_of_transmission_events_per_hour'],
    return HttpResponse('', status=status)
