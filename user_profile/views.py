from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import calendar
from django.utils import timezone
from .forms import ProfilePictureForm
from django.db.models import Count, Q, Case, When, IntegerField

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.userprofile
    
    today = timezone.now().date()
    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(today.year, today.month)
    submission_counts = profile.get_submission_calendar()

    processed_calendar = []
    for week in month_days:
        processed_week = []
        for day in week:
            count = submission_counts.get(day, 0)
            
            color_class = '' # Default is no specific color
            if count >= 5:
                color_class = 'cal-day-bg-high'
            elif count >= 3:
                color_class = 'cal-day-bg-med'
            elif count > 0:
                color_class = 'cal-day-bg-low'
            
            processed_day = {
                'date': day,
                'is_current_month': day.month == today.month,
                'count': count,
            }
            processed_week.append(processed_day)
        processed_calendar.append(processed_week)
    
    context = {
        'profile': profile,
        'calendar': processed_calendar,
        'month_name': today.strftime("%B"),
        'year': today.year
    }
    
    return render(request, 'user_profile/profile.html', context)

def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    # Ensure the logged-in user can only edit their own profile
    if request.user != user:
        return redirect('profile_view', username=request.user.username)

    if request.method == 'POST':
        # Pass request.POST and request.FILES to the form
        form = ProfilePictureForm(request.POST, request.FILES, instance=user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=user.username)
    else:
        form = ProfilePictureForm(instance=user.userprofile)

    context = {
        'form': form
    }
    return render(request, 'user_profile/edit_profile.html', context)

@login_required
def leaderboard_view(request):
    
    users_with_scores = User.objects.annotate(
        solved_easy=Count(
            'codesubmission__problem',
            filter=Q(codesubmission__verdict="Accepted", codesubmission__problem__difficulty='Easy'),
            distinct=True
        ),
        solved_medium=Count(
            'codesubmission__problem',
            filter=Q(codesubmission__verdict="Accepted", codesubmission__problem__difficulty='Medium'),
            distinct=True
        ),
        solved_hard=Count(
            'codesubmission__problem',
            filter=Q(codesubmission__verdict="Accepted", codesubmission__problem__difficulty='Hard'),
            distinct=True
        ),
        # You can create a weighted score for ranking
        total_score=Case(
            When(solved_easy__gt=0, then=1),
            When(solved_medium__gt=0, then=3),
            When(solved_hard__gt=0, then=5),
            default=0,
            output_field=IntegerField()
        ) * (Count('codesubmission__problem', filter=Q(codesubmission__verdict="Accepted"), distinct=True))
    ).filter(total_score__gt=0).order_by('-total_score')

    context = {
        'ranked_users': users_with_scores,
    }

    return render(request, 'user_profile/leaderboard.html', context)