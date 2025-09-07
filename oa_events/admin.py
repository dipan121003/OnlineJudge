from django.contrib import admin
from .models import Company, OAEvent, OAEventDiscussionComment

# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_display') # REMOVED 'slug'
    search_fields = ('name',)

    def logo_display(self, obj):
        if obj.logo:
            return '<img src="%s" width="50" height="50" style="object-fit: contain;" />' % obj.logo.url
        return "No Logo"
    logo_display.allow_tags = True
    logo_display.short_description = 'Logo'
    
@admin.register(OAEvent)
class OAEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'event_date', 'created_by', 'created_at')
    list_filter = ('company', 'event_date', 'created_at')
    search_fields = ('title', 'description', 'company__name')
    date_hierarchy = 'event_date'
    raw_id_fields = ('problems',) # For ManyToMany, easier to select if many problems
    fieldsets = (
        (None, {
            'fields': ('title', 'company', 'event_date', 'problems', 'description')
        }),
        ('Metadata', {
            'fields': ('created_by', 'ai_summary'),
            'classes': ('collapse',), # Collapsible section in admin
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
        
@admin.register(OAEventDiscussionComment)
class OAEventDiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'timestamp', 'is_spam', 'content_preview')
    list_filter = ('event', 'user', 'is_spam', 'timestamp')
    search_fields = ('content', 'user__username', 'event__title', 'event__company__name')
    raw_id_fields = ('user', 'event')
    actions = ['mark_as_spam', 'mark_as_not_spam']

    def content_preview(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    content_preview.short_description = 'Comment Content'

    def mark_as_spam(self, request, queryset):
        queryset.update(is_spam=True)
    mark_as_spam.short_description = "Mark selected comments as spam"

    def mark_as_not_spam(self, request, queryset):
        queryset.update(is_spam=False)
    mark_as_not_spam.short_description = "Mark selected comments as not spam"