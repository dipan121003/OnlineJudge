# backend/home/views.py
from django.shortcuts import render
from .models import Problem
from django.template import loader
from django.http import HttpResponse

def problems_list(request):
    # Fetch all problems, ordered however you like
    problems = Problem.objects.all().order_by('created_at')
    
    template = loader.get_template('problems.html')
    context = {}
    return HttpResponse(template.render(context,request))