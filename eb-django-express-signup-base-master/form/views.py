from django.http import HttpResponse
from django.shortcuts import render
from .models import Leads


def home(request):
    return render(request, 'index.html')


def signup(request):
    leads = Leads()
    status = leads.insert_lead(request.POST['email'],
                               request.POST['pop_size'],
                               request.POST['incubation_stage_duration'], request.POST['symptomatic_stage_duration'],
                               request.POST['min_fighting_duration'], request.POST['max_fighting_duration'],
                               request.POST['mortality_probability'],
                               request.POST['mean_number_of_transmission_events_per_hour'],
                               request.POST['app_installed_probability'], request.POST['contact_tracing_compliance'])

    # request.POST['mean_number_of_transmission_events_per_hour'],
    return HttpResponse('', status=status)
