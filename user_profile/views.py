from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import calendar
from django.utils import timezone

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