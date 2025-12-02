from django.db import models
from django.contrib.auth.models import User

# TODO: Phase 2 - Implement CustomUser model
# CustomUser should extend AbstractUser and include:
# - Additional fields: phone_number, profile_picture, bio, etc.
# - Custom manager for email-based authentication
# - Update AUTH_USER_MODEL in settings.py

# For now, using Django's default User model
# Register User model in admin for basic user management

class UserProfile(models.Model):
    """
    User profile model to extend default User model with roles
    """
    ROLE_CHOICES = (
        ('ENTERPRISE', 'Enterprise'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    # Staff details
    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
