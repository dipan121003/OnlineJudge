from django.shortcuts import render, get_object_or_404
from .models import Problem
from django.contrib.auth.decorators import login_required
from contest.models import Contest
from django.utils import timezone
from django.db.models import Q

def problems_list(request):
    search_query = request.GET.get('q', '')

    problems = Problem.objects.all()
    if search_query:
        problems = problems.filter(title__icontains=search_query)

    problems = problems.order_by('created_at')
    
    now = timezone.now()
    active_contests = Contest.objects.filter(start_time__lte=now, end_time__gte=now)
    upcoming_contests = Contest.objects.filter(start_time__gt=now).order_by('start_time')[:2] # Get the next 2 upcoming
    
    context = {
        'problems': problems,
        'active_contests': active_contests,
        'upcoming_contests': upcoming_contests,
        'search_query': search_query,
    }
    
    # Pass them into your template
    return render(request, 'problems.html', context)

@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    
    boilerplates = {
        'py': "# Your Python code here\n\ndef solve():\n    # Read input and solve the problem\n\n    pass\n\nsolve()\n",
        'cpp': "#include <iostream>\nusing namespace std;\n\n int main() {\n    // Your C++ code here\n\n    return 0;\n}\n"
    }
    
    submitted_code = ''
    submitted_language = 'py' 
    submitted_input = ''
    if request.method == 'POST':
        submitted_code = request.POST.get('code', '')
        submitted_language = request.POST.get('language', 'py')
        submitted_input = request.POST.get('input_data', '')
    else:
        submitted_code = boilerplates.get(submitted_language, '')

    context = {
        'problem': problem,
        'submitted_code': submitted_code,
        'submitted_language': submitted_language,
        'submitted_input': submitted_input,
        'boilerplates': boilerplates,
    }
    return render(request, 'problem_detail.html', context)