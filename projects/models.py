from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    """
    Organization model - represents a company/organization using CloudTask
    Created when an Enterprise user registers
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_organizations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Project(models.Model):
    """
    Project model - represents a software project within an organization
    Created by Enterprise admin, assigned to a Manager with a team
    """
    STATUS_CHOICES = (
        ('PLANNING', 'Planning'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='projects'
    )
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_projects'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    class Meta:
        ordering = ['-created_at']


class ProjectMember(models.Model):
    """
    ProjectMember model - links employees to projects as team members
    """
    ROLE_CHOICES = (
        ('DEVELOPER', 'Developer'),
        ('DESIGNER', 'Designer'),
        ('QA', 'QA Engineer'),
        ('DEVOPS', 'DevOps'),
        ('OTHER', 'Other'),
    )
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='members'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='project_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEVELOPER')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"
    
    class Meta:
        unique_together = ['project', 'user']
        ordering = ['joined_at']


class ProjectComment(models.Model):
    """
    ProjectComment model - for discussion threads on projects
    """
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='project_comments'
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}"
    
    class Meta:
        ordering = ['-created_at']
