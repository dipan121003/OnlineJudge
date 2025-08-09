# In contest/forms.py
from django import forms
from .models import SubAdminRequest, Contest, ContestProblem
from django.forms import modelformset_factory

class SubAdminRequestForm(forms.ModelForm):
    class Meta:
        model = SubAdminRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please explain why you would like to host a contest...'}),
        }
        
class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ['title', 'description', 'start_time', 'end_time']
        # Use Bootstrap's datetime-local input widgets
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        
class ContestProblemForm(forms.ModelForm):
    class Meta:
        model = ContestProblem
        fields = ['title', 'description', 'difficulty']
        
ContestProblemFormSet = modelformset_factory(
    ContestProblem,
    form=ContestProblemForm,
    extra=1, # Start with one empty problem form
    can_delete=True # Allow deleting problems
)