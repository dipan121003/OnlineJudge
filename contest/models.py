# In contest/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Model to store the main details of a contest
class Contest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # A helper property to quickly check if the contest is active
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

# Model for problems that are specific to a contest
class ContestProblem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    contest = models.ForeignKey(Contest, related_name='problems', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    # You can add fields like 'points' here later if you want

    def __str__(self):
        return f"{self.title} (Contest: {self.contest.title})"

# Model for test cases specific to a contest problem
class ContestTestCase(models.Model):
    problem = models.ForeignKey(ContestProblem, related_name='test_cases', on_delete=models.CASCADE)
    input_data = models.TextField()
    output_data = models.TextField()

    def __str__(self):
        return f"Test Case for {self.problem.title}"

# Model for users to register for a contest
class ContestRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only register for a contest once
        unique_together = ('user', 'contest')

    def __str__(self):
        return f"{self.user.username} registered for {self.contest.title}"

# Model to handle requests from users to become sub-admins/contest creators
class SubAdminRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField() # A field for the user to explain why they want to host
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.user.username} ({self.status})"

class ContestSubmission(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    problem = models.ForeignKey(ContestProblem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=50)
    code = models.TextField()
    verdict = models.CharField(max_length=100, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username} for {self.problem.title} in {self.contest.title}"