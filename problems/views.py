# backend/home/views.py
from django.shortcuts import render
from .models import Problem
from django.http import HttpResponse

def problems_list(request):
    # Fetch all problems, ordered however you like
    problems = Problem.objects.all().order_by('created_at')
    
    # Pass them into your template
    return render(request, 'problems.html', {
        'problems': problems
    })
    

