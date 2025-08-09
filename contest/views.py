# In contest/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .forms import SubAdminRequestForm, ContestForm, ContestProblemFormSet
from .models import SubAdminRequest, ContestProblem, Contest, ContestRegistration, ContestSubmission
from submission.views import run_code




def is_contest_creator(user):
    return user.groups.filter(name='Contest Creator').exists()

def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = ContestRegistration.objects.filter(user=request.user, contest=contest).exists()

    context = {
        'contest': contest,
        'is_registered': is_registered,
    }
    return render(request, 'contest/contest_detail.html', context)

@login_required
def request_sub_admin(request):
    # Check if the user already has a pending or approved request
    existing_request = SubAdminRequest.objects.filter(user=request.user, status__in=['Pending', 'Approved']).first()

    if request.method == 'POST':
        form = SubAdminRequestForm(request.POST)
        if form.is_valid() and not existing_request:
            sub_admin_request = form.save(commit=False)
            sub_admin_request.user = request.user
            sub_admin_request.save()
            return redirect('request_sub_admin_success') # Redirect to a success page
    else:
        form = SubAdminRequestForm()

    context = {
        'form': form,
        'existing_request': existing_request,
    }
    return render(request, 'contest/request_form.html', context)

@login_required
def request_sub_admin_success(request):
    return render(request, 'contest/request_success.html')


@login_required
@user_passes_test(is_contest_creator) # Restrict access to contest creators
def create_contest(request):
    if request.method == 'POST':
        contest_form = ContestForm(request.POST)
        problem_formset = ContestProblemFormSet(request.POST, queryset=ContestProblem.objects.none())

        if contest_form.is_valid() and problem_formset.is_valid():
            # Save the main contest form
            contest = contest_form.save(commit=False)
            contest.created_by = request.user
            contest.save()

            # Save the problem forms, linking them to the new contest
            problems = problem_formset.save(commit=False)
            for problem in problems:
                problem.contest = contest
                problem.save()

            # Handle deleted forms
            for form in problem_formset.deleted_forms:
                form.instance.delete()

            # Redirect to a page where they can add test cases (we'll build this next)
            return redirect('some_success_page_for_now') 
    else:
        contest_form = ContestForm()
        problem_formset = ContestProblemFormSet(queryset=ContestProblem.objects.none())

    context = {
        'contest_form': contest_form,
        'problem_formset': problem_formset,
    }
    return render(request, 'contest/create_contest.html', context)

def contest_list(request):
    now = timezone.now()

    # Get all contests and categorize them
    all_contests = Contest.objects.all().order_by('start_time')
    upcoming_contests = all_contests.filter(start_time__gt=now)
    active_contests = all_contests.filter(start_time__lte=now, end_time__gte=now)
    past_contests = all_contests.filter(end_time__lt=now)

    context = {
        'upcoming_contests': upcoming_contests,
        'active_contests': active_contests,
        'past_contests': past_contests,
    }

    return render(request, 'contest/contest_list.html', context)

@login_required
def register_for_contest(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    # Use get_or_create to prevent duplicate registrations
    ContestRegistration.objects.get_or_create(user=request.user, contest=contest)
    return redirect('contest_detail', contest_id=contest.id)

@login_required
def contest_interface(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # Security Checks: Ensure user is registered and contest is active
    if not contest.is_active:
        return HttpResponseForbidden("This contest is not currently active.")
    if not ContestRegistration.objects.filter(user=request.user, contest=contest).exists():
        return HttpResponseForbidden("You are not registered for this contest.")

    # Get all problems for this contest
    problems = contest.problems.all()

    context = {
        'contest': contest,
        'problems': problems,
    }
    return render(request, 'contest/contest_interface.html', context)

@login_required
def submit_contest_problem(request, contest_id, problem_id):
    contest = get_object_or_404(Contest, id=contest_id)
    problem = get_object_or_404(ContestProblem, id=problem_id)

    # Security checks
    if not contest.is_active or not ContestRegistration.objects.filter(user=request.user, contest=contest).exists():
        return HttpResponseForbidden("You cannot submit to this contest at this time.")

    if request.method == 'POST':
        language = request.POST.get('language')
        code = request.POST.get('code')

        # Determine the verdict
        final_verdict = "Accepted"
        test_cases = problem.test_cases.all()
        # ... (Add your full verdict checking logic here, same as your main submit_solution view) ...

        # Create the contest submission record
        ContestSubmission.objects.create(
            contest=contest,
            problem=problem,
            user=request.user,
            language=language,
            code=code,
            verdict=final_verdict
        )
        # Redirect back to the contest interface
        return redirect('contest_interface', contest_id=contest.id)

    return redirect('contest_interface', contest_id=contest.id)