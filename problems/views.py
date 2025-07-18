from django.shortcuts import render
from .models import Problem

def problems_list(request):
    # Fetch all problems, ordered however you like
    problems = Problem.objects.all().order_by('created_at')
    
    # Pass them into your template
    return render(request, 'problems.html', {
        'problems': problems
    })

def problem_detail(request, problem_id):
    # Fetch a specific problem by its ID
    problem = Problem.objects.get(id=problem_id)
    
    # Pass the problem into your template
    return render(request, 'problem_detail.html', {
        'problem': problem
    })