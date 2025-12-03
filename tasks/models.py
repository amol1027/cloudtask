import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project


def task_attachment_path(instance, filename):
    """Generate upload path for task attachments"""
    return f'tasks/{instance.task.project.id}/{instance.task.id}/{filename}'


class Task(models.Model):
    """
    Task model - represents a task within a project
    Created by Managers, assigned to Employees
    """
    STATUS_CHOICES = (
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('IN_REVIEW', 'In Review'),
        ('DONE', 'Done'),
    )
    
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    due_date = models.DateField(null=True, blank=True)
    
    # Task dependencies - tasks that must be completed before this one
    depends_on = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='blocking'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.project.name})"
    
    @property
    def is_blocked(self):
        """Check if task is blocked by incomplete dependencies"""
        return self.depends_on.exclude(status='DONE').exists()
    
    @property
    def blocking_tasks(self):
        """Get tasks that are blocking this one"""
        return self.depends_on.exclude(status='DONE')
    
    class Meta:
        ordering = ['-created_at']


class TaskComment(models.Model):
    """
    TaskComment model - for progress updates and comments on tasks
    Employees can update progress, Managers can provide feedback
    """
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='task_comments'
    )
    comment = models.TextField()
    # Optional: track status change with the comment
    status_changed_to = models.CharField(
        max_length=20, 
        choices=Task.STATUS_CHOICES, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"
    
    class Meta:
        ordering = ['created_at']


class Tag(models.Model):
    """
    Tag model - for categorizing tasks
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6366f1')  # Hex color code
    
    def __str__(self):
        return self.name


class TaskAttachment(models.Model):
    """
    TaskAttachment model - for file uploads on tasks
    """
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(upload_to=task_attachment_path)
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)  # in bytes
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='uploaded_attachments'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} on {self.task.title}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.filename = os.path.basename(self.file.name)
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def file_size_display(self):
        """Return human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    @property
    def file_extension(self):
        """Return file extension"""
        return os.path.splitext(self.filename)[1].lower()
    
    class Meta:
        ordering = ['-uploaded_at']


class TimeEntry(models.Model):
    """
    TimeEntry model - for tracking time spent on tasks
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    description = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)  # Calculated or manual
    is_running = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.duration_display})"
    
    def save(self, *args, **kwargs):
        # Calculate duration if end_time is set
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            self.is_running = False
        super().save(*args, **kwargs)
    
    def stop(self):
        """Stop the timer"""
        self.end_time = timezone.now()
        self.save()
    
    @property
    def duration_display(self):
        """Return human-readable duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    class Meta:
        ordering = ['-start_time']


class TaskTemplate(models.Model):
    """
    TaskTemplate model - reusable task configurations
    """
    PRIORITY_CHOICES = Task.PRIORITY_CHOICES
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    default_title = models.CharField(max_length=200)
    default_description = models.TextField(blank=True)
    default_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    estimated_hours = models.PositiveIntegerField(default=0, help_text="Estimated hours to complete")
    
    # Template belongs to an organization
    organization = models.ForeignKey(
        'projects.Organization',
        on_delete=models.CASCADE,
        related_name='task_templates'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
