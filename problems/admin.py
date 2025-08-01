from django.contrib import admin

# Register your models here.
from .models import Problem, TestCase

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'created_at')
    search_fields = ('title',)
    
admin.site.register(TestCase)