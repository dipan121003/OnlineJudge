from django.shortcuts import render, get_object_or_404
from .models import Problem
from django.contrib.auth.decorators import login_required
from contest.models import Contest
from django.utils import timezone

def problems_list(request):
    # Fetch all problems, ordered however you like
    problems = Problem.objects.all().order_by('created_at')
    
    now = timezone.now()
    active_contests = Contest.objects.filter(start_time__lte=now, end_time__gte=now)
    upcoming_contests = Contest.objects.filter(start_time__gt=now).order_by('start_time')[:2] # Get the next 2 upcoming
    
    context = {
        'problems': problems,
        'active_contests': active_contests,
        'upcoming_contests': upcoming_contests,
    }
    
    # Pass them into your template
    return render(request, 'problems.html', context)

@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    
    submitted_code = ''
    submitted_language = 'py' 
    submitted_input = ''
    if request.method == 'POST':
        submitted_code = request.POST.get('code', '')
        submitted_language = request.POST.get('language', 'py')
        submitted_input = request.POST.get('input_data', '')

    context = {
        'problem': problem,
        'submitted_code': submitted_code,
        'submitted_language': submitted_language,
        'submitted_input': submitted_input,
    }
    return render(request, 'problem_detail.html', context)