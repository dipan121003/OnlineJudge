from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem

# Create your models here.
class CodeSubmission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=50)
    input_data = models.TextField(null=True,blank=True)
    output_data = models.TextField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Submission by {self.user.username} for Problem {self.problem_id}'