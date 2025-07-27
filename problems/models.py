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
    
class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem, 
        on_delete=models.CASCADE, 
        related_name='test_cases'
    )
    input_data = models.TextField()
    output_data = models.TextField()

    def __str__(self):
        # This will give a helpful name in the admin panel
        return f"Test Case for {self.problem.title}"