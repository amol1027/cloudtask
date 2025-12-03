from django.contrib import admin
from .models import Task, TaskComment, Tag, TaskAttachment


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ('user', 'created_at')


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = ('uploaded_by', 'uploaded_at', 'file_size')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'due_date', 'assigned_to', 'created_by')
    list_filter = ('status', 'priority', 'project', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    filter_horizontal = ('depends_on',)
    inlines = [TaskCommentInline, TaskAttachmentInline]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'status_changed_to', 'created_at')
    list_filter = ('status_changed_to', 'created_at')
    search_fields = ('comment', 'task__title', 'user__username')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'task', 'uploaded_by', 'file_size', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'task__title')
