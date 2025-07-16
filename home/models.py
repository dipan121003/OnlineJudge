from django.db import models

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

class TestCase(models.Model):
    problem     = models.ForeignKey(Problem, related_name='test_cases',
                                    on_delete=models.CASCADE)
    input_data  = models.TextField()
    output_data = models.TextField()

    def __str__(self):
        return f"TC #{self.id} for {self.problem.title}"
    