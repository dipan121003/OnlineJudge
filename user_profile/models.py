from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay
from submission.models import CodeSubmission
from problems.models import Problem

# Create your models here.
class  UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    @property
    def solved_easy(self):
        return CodeSubmission.objects.filter(
            user=self.user, 
            verdict="Accepted",
            problem__difficulty='Easy'
        ).values('problem').distinct().count()

    @property
    def solved_medium(self):
        return CodeSubmission.objects.filter(
            user=self.user, 
            verdict="Accepted",
            problem__difficulty='Medium'
        ).values('problem').distinct().count()

    @property
    def solved_hard(self):
        return CodeSubmission.objects.filter(
            user=self.user, 
            verdict="Accepted",
            problem__difficulty='Hard'
        ).values('problem').distinct().count()
        
    def get_submission_calendar(self):
        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=31)

        submissions = CodeSubmission.objects.filter(
            user=self.user,
            verdict="Accepted",
            timestamp__range=[start_date, end_date]
        ).annotate(
            day=TruncDay('timestamp')
        ).values('day').annotate(
            count=Count('problem', distinct=True)
        ).values('day', 'count')
        
        return {item['day'].date(): item['count'] for item in submissions}