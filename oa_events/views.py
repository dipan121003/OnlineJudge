from django.shortcuts import render, get_object_or_404, redirect
from .models import OAEvent, OAEventDiscussionComment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
import json
import re # For basic spam filtering

# Define constants for comment restrictions
MAX_COMMENTS_PER_EVENT_PER_USER = 10
MAX_COMMENT_LENGTH = 500
MIN_COMMENT_LENGTH = 1
# Basic spam keywords (expand this list as needed)
SPAM_KEYWORDS = ['http://', 'https://', 'www.', '.com', '.ru', 'buy now', 'free money', 'sex', 'viagra']

# Create your views here.
def oa_event_list(request):
    """
    Displays a list of all Company OA/Interview Events.
    """
    events = OAEvent.objects.all().order_by('-event_date', 'company__name') # Order by latest events first
    context = {
        'events': events,
        'page_title': "Company OA/Interview Events"
    }
    return render(request, 'oa_events/oa_event_list.html', context)

@login_required
def oa_event_detail(request, event_id):
    """
    Displays the details of a specific OA/Interview Event,
    including its problems, discussion section, and handles comment submission.
    """
    event = get_object_or_404(OAEvent.objects.select_related('company').prefetch_related('problems'), id=event_id)
    
    comments = OAEventDiscussionComment.objects.filter(event=event, is_spam=False).order_by('timestamp').select_related('user')
    user_comments_count = OAEventDiscussionComment.objects.filter(event=event, user=request.user).count()
    
    remaining_comments_count = MAX_COMMENTS_PER_EVENT_PER_USER - user_comments_count
    if remaining_comments_count < 0: # Should not happen with proper logic, but good safeguard
        remaining_comments_count = 0
    
    comment_error = None
    if request.method == 'POST':
        # Check if it's an AJAX request (for dynamic comment submission)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = json.loads(request.body)
            comment_content = data.get('content', '').strip()
        else: # Standard form submission
            comment_content = request.POST.get('comment_content', '').strip()

        # --- Comment Restrictions & Validation ---
        if user_comments_count >= MAX_COMMENTS_PER_EVENT_PER_USER:
            comment_error = f"You have reached the maximum of {MAX_COMMENTS_PER_EVENT_PER_USER} comments for this event."
        elif not (MIN_COMMENT_LENGTH <= len(comment_content) <= MAX_COMMENT_LENGTH):
            comment_error = f"Comment must be between {MIN_COMMENT_LENGTH} and {MAX_COMMENT_LENGTH} characters long."
        else:
            is_spam_flag = False
            for keyword in SPAM_KEYWORDS:
                if keyword in comment_content.lower():
                    is_spam_flag = True
                    break
            
            # Create the comment
            OAEventDiscussionComment.objects.create(
                event=event,
                user=request.user,
                content=comment_content,
                is_spam=is_spam_flag # Flag for admin review if potential spam
            )
            # Increment count for immediate display, as we just added one
            user_comments_count += 1 

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # For AJAX, return the new comment data
                new_comment = OAEventDiscussionComment.objects.filter(event=event, user=request.user).order_by('-timestamp').first()
                return JsonResponse({
                    'success': True,
                    'comment_html': render(request, 'oa_events/_comment.html', {'comment': new_comment}).content.decode('utf-8'),
                    'user_comments_count': user_comments_count,
                    'max_comments': MAX_COMMENTS_PER_EVENT_PER_USER,
                })
            else:
                # For standard form submission, redirect to prevent resubmission on refresh
                return redirect('oa_events:oa_event_detail', event_id=event.id)
        
        # If there's an error and it's an AJAX request, return JSON error
        if comment_error and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': comment_error}, status=400)


    context = {
        'event': event,
        'page_title': f"{event.title} - {event.company.name}",
        'comments': comments,
        'user_comments_count': user_comments_count,
        'max_comments_per_event_per_user': MAX_COMMENTS_PER_EVENT_PER_USER,
        'max_comment_length': MAX_COMMENT_LENGTH,
        'min_comment_length': MIN_COMMENT_LENGTH,
        'comment_error': comment_error,
        'remaining_comments_count': remaining_comments_count,
    }
    return render(request, 'oa_events/oa_event_detail.html', context)
