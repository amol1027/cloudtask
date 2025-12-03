from django.contrib import admin
from .models import Organization, Project, ProjectMember, ProjectComment


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1


class ProjectCommentInline(admin.TabularInline):
    model = ProjectComment
    extra = 0
    readonly_fields = ('user', 'created_at')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'manager', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'organization', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ProjectMemberInline, ProjectCommentInline]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'joined_at')
    list_filter = ('role', 'project')
    search_fields = ('user__username', 'project__name')


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'created_at')
    list_filter = ('created_at', 'project')
    search_fields = ('comment', 'project__name', 'user__username')
