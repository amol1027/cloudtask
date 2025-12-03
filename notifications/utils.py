"""
Utility functions for creating notifications and logging activities
"""
from django.urls import reverse
from .models import Notification, ActivityLog


def notify_task_assigned(task, assigned_by):
    """Create notification when a task is assigned to someone"""
    recipients = set()
    
    # Notify assignee
    if task.assigned_to and task.assigned_to != assigned_by:
        recipients.add(task.assigned_to)
    
    # Notify project manager
    if task.project.manager and task.project.manager != assigned_by:
        recipients.add(task.project.manager)
    
    for recipient in recipients:
        Notification.create_notification(
            recipient=recipient,
            notification_type='TASK_ASSIGNED',
            title='Task Assignment',
            message=f'"{task.title}" has been assigned to {task.assigned_to.get_full_name() or task.assigned_to.username}',
            link=reverse('tasks:detail', kwargs={'pk': task.pk})
        )


def notify_task_created(task, created_by):
    """Create notification when a new task is created"""
    recipients = set()
    
    # Notify project manager (if not the creator)
    if task.project.manager and task.project.manager != created_by:
        recipients.add(task.project.manager)
    
    # Notify project creator/owner (enterprise user)
    if task.project.created_by and task.project.created_by != created_by:
        recipients.add(task.project.created_by)
    
    for recipient in recipients:
        Notification.create_notification(
            recipient=recipient,
            notification_type='TASK_UPDATED',
            title='New Task Created',
            message=f'New task "{task.title}" was created in project "{task.project.name}"',
            link=reverse('tasks:detail', kwargs={'pk': task.pk})
        )


def notify_task_updated(task, updated_by):
    """Create notification when a task is updated"""
    recipients = set()
    
    # Notify assignee
    if task.assigned_to and task.assigned_to != updated_by:
        recipients.add(task.assigned_to)
    
    # Notify task creator
    if task.created_by and task.created_by != updated_by:
        recipients.add(task.created_by)
    
    # Notify project manager
    if task.project.manager and task.project.manager != updated_by:
        recipients.add(task.project.manager)
    
    for recipient in recipients:
        Notification.create_notification(
            recipient=recipient,
            notification_type='TASK_UPDATED',
            title='Task Updated',
            message=f'Task "{task.title}" has been updated',
            link=reverse('tasks:detail', kwargs={'pk': task.pk})
        )


def notify_task_comment(comment, commenter):
    """Create notification when someone comments on a task"""
    task = comment.task
    recipients = set()
    
    # Notify assignee
    if task.assigned_to and task.assigned_to != commenter:
        recipients.add(task.assigned_to)
    
    # Notify task creator
    if task.created_by and task.created_by != commenter:
        recipients.add(task.created_by)
    
    # Notify project manager
    if task.project.manager and task.project.manager != commenter:
        recipients.add(task.project.manager)
    
    # Notify other commenters
    for prev_comment in task.comments.exclude(user=commenter).select_related('user'):
        recipients.add(prev_comment.user)
    
    for recipient in recipients:
        Notification.create_notification(
            recipient=recipient,
            notification_type='TASK_COMMENTED',
            title='New Comment on Task',
            message=f'{commenter.get_full_name() or commenter.username} commented on "{task.title}"',
            link=reverse('tasks:detail', kwargs={'pk': task.pk})
        )


def notify_project_member_added(project, member_user, added_by):
    """Create notification when someone is added to a project"""
    recipients = set()
    
    # Notify the new member
    if member_user != added_by:
        recipients.add(member_user)
    
    # Notify project manager
    if project.manager and project.manager != added_by and project.manager != member_user:
        recipients.add(project.manager)
    
    # Notify project creator/owner (enterprise)
    if project.created_by and project.created_by != added_by and project.created_by != member_user:
        recipients.add(project.created_by)
    
    for recipient in recipients:
        if recipient == member_user:
            Notification.create_notification(
                recipient=recipient,
                notification_type='PROJECT_ASSIGNED',
                title='Added to Project',
                message=f'You have been added to project "{project.name}"',
                link=reverse('projects:detail', kwargs={'pk': project.pk})
            )
        else:
            Notification.create_notification(
                recipient=recipient,
                notification_type='PROJECT_UPDATED',
                title='New Team Member',
                message=f'{member_user.get_full_name() or member_user.username} was added to project "{project.name}"',
                link=reverse('projects:detail', kwargs={'pk': project.pk})
            )


def notify_project_created(project, created_by):
    """Create notification when a project is created (for enterprise admins)"""
    # Notify organization's enterprise users (admins)
    from accounts.models import UserProfile
    
    if project.organization:
        enterprise_users = UserProfile.objects.filter(
            organization=project.organization,
            role='ENTERPRISE'
        ).exclude(user=created_by).select_related('user')
        
        for profile in enterprise_users:
            Notification.create_notification(
                recipient=profile.user,
                notification_type='PROJECT_UPDATED',
                title='New Project Created',
                message=f'New project "{project.name}" was created by {created_by.get_full_name() or created_by.username}',
                link=reverse('projects:detail', kwargs={'pk': project.pk})
            )


def notify_project_updated(project, updated_by):
    """Create notification when a project is updated"""
    recipients = set()
    
    # Notify project manager
    if project.manager and project.manager != updated_by:
        recipients.add(project.manager)
    
    # Notify project creator/owner
    if project.created_by and project.created_by != updated_by:
        recipients.add(project.created_by)
    
    for recipient in recipients:
        Notification.create_notification(
            recipient=recipient,
            notification_type='PROJECT_UPDATED',
            title='Project Updated',
            message=f'Project "{project.name}" has been updated',
            link=reverse('projects:detail', kwargs={'pk': project.pk})
        )


def notify_project_comment(comment, commenter):
    """Create notification when someone comments on a project"""
    project = comment.project
    recipients = set()
    
    # Notify project manager
    if project.manager and project.manager != commenter:
        recipients.add(project.manager)
    
    # Notify project creator
    if project.created_by != commenter:
        recipients.add(project.created_by)
    
    # Notify project members
    for member in project.members.exclude(user=commenter).select_related('user'):
        recipients.add(member.user)
    
    for recipient in recipients:
        Notification.create_notification(
            recipient=recipient,
            notification_type='PROJECT_COMMENTED',
            title='New Comment on Project',
            message=f'{commenter.get_full_name() or commenter.username} commented on "{project.name}"',
            link=reverse('projects:detail', kwargs={'pk': project.pk})
        )


def log_task_activity(task, user, action, description, old_value=None, new_value=None):
    """Log task-related activity"""
    org_id = None
    if hasattr(user, 'profile') and user.profile.organization:
        org_id = user.profile.organization.id
    
    ActivityLog.log_activity(
        user=user,
        action=action,
        entity_type='TASK',
        entity_id=task.pk,
        entity_name=task.title,
        description=description,
        organization_id=org_id,
        old_value=old_value,
        new_value=new_value
    )


def log_project_activity(project, user, action, description, old_value=None, new_value=None):
    """Log project-related activity"""
    org_id = project.organization.id if project.organization else None
    
    ActivityLog.log_activity(
        user=user,
        action=action,
        entity_type='PROJECT',
        entity_id=project.pk,
        entity_name=project.name,
        description=description,
        organization_id=org_id,
        old_value=old_value,
        new_value=new_value
    )
