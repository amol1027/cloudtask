from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile

class StaffCreationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.add_manager_url = reverse('accounts:add_manager')
        self.add_employee_url = reverse('accounts:add_employee')
        self.dashboard_url = reverse('dashboard:index')
        
        # Create Enterprise User
        self.enterprise_user = User.objects.create_user(username='enterprise', password='password123')
        UserProfile.objects.create(user=self.enterprise_user, role='ENTERPRISE')
        
        # Login
        self.client.force_login(self.enterprise_user)

    def test_add_manager(self):
        """Test adding a manager account"""
        response = self.client.post(self.add_manager_url, {
            'username': 'manager1',
            'first_name': 'Manager',
            'last_name': 'One',
            'email': 'manager1@example.com',
            'department': 'Sales',
            'staff_id': 'MGR001',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        
        if response.status_code == 200:
            print(response.context['form'].errors)
            
        self.assertRedirects(response, self.dashboard_url)
        
        # Verify user created
        manager = User.objects.get(username='manager1')
        self.assertEqual(manager.profile.role, 'MANAGER')
        self.assertEqual(manager.profile.staff_id, 'MGR001')
        self.assertEqual(manager.profile.department, 'Sales')

    def test_add_employee(self):
        """Test adding an employee account"""
        response = self.client.post(self.add_employee_url, {
            'username': 'emp1',
            'first_name': 'Employee',
            'last_name': 'One',
            'email': 'emp1@example.com',
            'department': 'IT',
            'staff_id': 'EMP001',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        
        self.assertRedirects(response, self.dashboard_url)
        
        # Verify user created
        emp = User.objects.get(username='emp1')
        self.assertEqual(emp.profile.role, 'EMPLOYEE')
        self.assertEqual(emp.profile.staff_id, 'EMP001')
        self.assertEqual(emp.profile.department, 'IT')

    def test_non_enterprise_cannot_add_staff(self):
        """Test that non-enterprise users cannot add staff"""
        # Create Manager User
        manager_user = User.objects.create_user(username='manager_user', password='password123')
        UserProfile.objects.create(user=manager_user, role='MANAGER')
        self.client.force_login(manager_user)
        
        response = self.client.get(self.add_manager_url)
        self.assertEqual(response.status_code, 403) # PermissionDenied
