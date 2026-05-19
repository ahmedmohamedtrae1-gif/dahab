from django.contrib import admin
from .models import DynamicForm, FormField, FormSubmission, FormAnswer

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1

@admin.register(DynamicForm)
class DynamicFormAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'submissions_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FormFieldInline]

    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = 'عدد الردود'

class FormAnswerInline(admin.TabularInline):
    model = FormAnswer
    extra = 0
    readonly_fields = ['field_label', 'value']
    can_delete = False

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form', 'created_at', 'ip_address']
    list_filter = ['form', 'created_at']
    search_fields = ['answers__value', 'answers__field_label']
    readonly_fields = ['form', 'created_at', 'ip_address', 'user_agent']
    inlines = [FormAnswerInline]

admin.site.register(FormField)
