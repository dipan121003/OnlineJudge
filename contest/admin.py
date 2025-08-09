# In contest/admin.py
from django.contrib import admin
from .models import Contest, ContestProblem, ContestTestCase, SubAdminRequest, ContestRegistration

@admin.register(SubAdminRequest)
class SubAdminRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'requested_at')
    list_filter = ('status',)
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        # This action will approve the request and add the user to the "Contest Creator" group
        from django.contrib.auth.models import Group
        contest_creator_group, created = Group.objects.get_or_create(name='Contest Creator')

        for req in queryset:
            req.user.groups.add(contest_creator_group)
            req.status = 'Approved'
            req.save()

    approve_requests.short_description = "Approve selected requests and make user a Contest Creator"

# Register other models for basic admin access
admin.site.register(Contest)
admin.site.register(ContestProblem)
admin.site.register(ContestTestCase)
admin.site.register(ContestRegistration)