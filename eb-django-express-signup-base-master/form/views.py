from django.http import HttpResponse
from django.shortcuts import render
from .models import Leads


def home(request):
    return render(request, 'index.html')


def signup(request):
    leads = Leads()
    status = leads.insert_lead(request.POST['MessageGroupId'], request.POST['id'], request.POST['pop_size'], request.POST['lockdownFlag'])
    return HttpResponse('', status=status)
