from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    User profile model to extend default User model with roles and organization
    """
    ROLE_CHOICES = (
        ('ENTERPRISE', 'Enterprise'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    # Organization - links all users (Enterprise, Manager, Employee) to their organization
    # For Enterprise users, this is set when they create an organization
    # For Managers/Employees, this is set when Enterprise admin adds them
    organization = models.ForeignKey(
        'projects.Organization',
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True
    )
    
    # Staff details
    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    @property
    def is_enterprise(self):
        return self.role == 'ENTERPRISE'
    
    @property
    def is_manager(self):
        return self.role == 'MANAGER'
    
    @property
    def is_employee(self):
        return self.role == 'EMPLOYEE'
