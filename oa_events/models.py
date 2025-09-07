from django.db import models
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the company (e.g., Google, Amazon)")
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True,
                             help_text="Upload company logo (optional)")

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class OAEvent(models.Model):
    title = models.CharField(max_length=200, help_text="e.g., Google OA Round, Amazon SDE Interview")
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                help_text="Which company conducted this event?")
    event_date = models.DateField(help_text="When did this OA/Interview take place?")
    problems = models.ManyToManyField('problems.Problem', related_name='oa_events',
                                      help_text="Select problems featured in this event.")
    description = models.TextField(blank=True,
                                   help_text="General notes or observations about the event (optional).")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # NEW FIELD: For storing the AI-generated summary
    ai_summary = models.TextField(null=True, blank=True,
                                  help_text="AI-generated summary of key concepts from discussions.")


    class Meta:
        verbose_name = "OA/Interview Event"
        verbose_name_plural = "OA/Interview Events"
        ordering = ['-event_date', 'company__name', 'title'] # Order by latest events first
        unique_together = ('company', 'event_date', 'title') # Prevent duplicate events for same company/date/title

    def __str__(self):
        return f"{self.title} ({self.company.name} - {self.event_date})"
    

class OAEventDiscussionComment(models.Model):
    event = models.ForeignKey(OAEvent, on_delete=models.CASCADE, related_name='discussion_comments',
                              help_text="The OA Event this comment belongs to.")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             help_text="The user who posted this comment.")
    content = models.TextField(help_text="The content of the discussion comment.")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the comment was posted.")
    is_spam = models.BooleanField(default=False, help_text="Flag for potential spam (for moderation).")

    class Meta:
        verbose_name = "OA Event Discussion Comment"
        verbose_name_plural = "OA Event Discussion Comments"
        ordering = ['timestamp']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.event.title} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
