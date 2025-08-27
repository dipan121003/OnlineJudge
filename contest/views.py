# In contest/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from .forms import SubAdminRequestForm, ContestForm, ContestProblemFormSet
from .models import SubAdminRequest, ContestProblem, Contest, ContestRegistration, ContestSubmission, ContestTestCase
from submission.views import run_code
from django.forms import modelformset_factory


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
@permission_required('contest.add_contest', login_url='/auth/login/') # Restrict access to contest creators
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
            return redirect('contest_list') 
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
    
    boilerplates = {
        'py': 'def solve():\n    # Your code here\n\n    pass\n\nsolve()',
        'cpp': '#include <iostream>\n\nint main() {\n    // Your code here\n\n    return 0;\n}',
    }

    context = {
        'contest': contest,
        'problems': problems,
        'boilerplates': boilerplates,
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

        # --- MODIFICATION: Added the full verdict checking logic ---
        final_verdict = "Accepted"
        test_cases = problem.test_cases.all()

        if not test_cases.exists():
            final_verdict = "System Error: No Test Cases"
        else:
            for case in test_cases:
                # Use your existing run_code utility for each test case
                # Note: We're not setting a memory limit here, but you could add it
                output = run_code(language, code, case.input_data)
                
                # Check for execution errors first
                if "Error" in output or "Timed Out" in output:
                    final_verdict = output # Set verdict to the error message
                    break # Stop checking other test cases

                # Check if the code's output matches the test case's expected output
                if output.strip() != case.output_data.strip():
                    final_verdict = "Wrong Answer"
                    break # Stop on the first wrong answer
        # --- End of added logic ---

        # Create the contest submission record with the correct verdict
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

@login_required
@permission_required('contest.add_contest', login_url='/auth/login/')
def manage_my_contests(request):
    contests = Contest.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'contest/manage_my_contests.html', {'contests': contests})

@login_required
def manage_contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id, created_by=request.user)

    # We will create a simple formset for test cases
    TestCaseFormSet = modelformset_factory(
        ContestTestCase, 
        fields=('input_data', 'output_data'), 
        extra=1, 
        can_delete=True
    )

    if request.method == 'POST':
        # This logic handles adding/editing test cases for a specific problem
        problem_id = request.POST.get('problem_id')
        problem = get_object_or_404(ContestProblem, id=problem_id, contest=contest)
        
        formset_prefix = f'testcases-{problem.id}'
        formset = TestCaseFormSet(request.POST, queryset=problem.test_cases.all(), prefix=formset_prefix)

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.problem = problem
                instance.save()
            formset.save_m2m() # Important for many-to-many relationships if any

            # Handle deleted forms
            for form in formset.deleted_forms:
                form.instance.delete()

            return redirect('manage_contest_detail', contest_id=contest.id)

    # Prepare a dictionary of formsets, one for each problem
    problem_formsets = {}
    for problem in contest.problems.all():
        formset_prefix = f'testcases-{problem.id}'
        problem_formsets[problem.id] = TestCaseFormSet(queryset=problem.test_cases.all(), prefix=formset_prefix)

    context = {
        'contest': contest,
        'problem_formsets': problem_formsets,
    }
    return render(request, 'contest/manage_contest_detail.html', context)

def my_contest_submissions(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # Get all of the current user's submissions for this contest
    submissions = ContestSubmission.objects.filter(
        user=request.user,
        contest=contest
    ).order_by('-submitted_at')

    context = {
        'contest': contest,
        'submissions': submissions,
    }
    return render(request, 'contest/contest_submissions.html', context)