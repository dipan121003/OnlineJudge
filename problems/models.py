from django.db import models

# Create your models here.
class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    title       = models.CharField(max_length=200)
    description = models.TextField()
    difficulty  = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    created_at  = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title 