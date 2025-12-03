from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """
    Notification model - for alerting users about important events
    """
    TYPE_CHOICES = (
        ('TASK_ASSIGNED', 'Task Assigned'),
        ('TASK_UPDATED', 'Task Updated'),
        ('TASK_COMMENTED', 'Task Comment'),
        ('PROJECT_ASSIGNED', 'Added to Project'),
        ('PROJECT_UPDATED', 'Project Updated'),
        ('PROJECT_COMMENTED', 'Project Comment'),
        ('MENTION', 'Mentioned'),
        ('DEADLINE', 'Deadline Reminder'),
    )
    
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Generic link to related object
    link = models.CharField(max_length=255, blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"
    
    class Meta:
        ordering = ['-created_at']
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, link=None):
        """Helper method to create notifications"""
        return cls.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )


class ActivityLog(models.Model):
    """
    ActivityLog model - tracks all changes to projects and tasks
    """
    ACTION_CHOICES = (
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('STATUS_CHANGE', 'Status Changed'),
        ('ASSIGN', 'Assigned'),
        ('COMMENT', 'Commented'),
        ('ATTACH', 'Attached File'),
    )
    
    ENTITY_CHOICES = (
        ('PROJECT', 'Project'),
        ('TASK', 'Task'),
        ('COMMENT', 'Comment'),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    entity_id = models.PositiveIntegerField()
    entity_name = models.CharField(max_length=200)
    
    # Optional: store old and new values for changes
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    
    # Link to organization for filtering
    organization_id = models.PositiveIntegerField(null=True, blank=True)
    
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.entity_type}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activity logs'
    
    @classmethod
    def log_activity(cls, user, action, entity_type, entity_id, entity_name, 
                     description, organization_id=None, old_value=None, new_value=None):
        """Helper method to log activities"""
        return cls.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            organization_id=organization_id,
            old_value=old_value,
            new_value=new_value
        )
