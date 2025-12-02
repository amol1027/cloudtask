from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile

class RoleBasedLoginTests(TestCase):
    """Test role-based login validation"""
    
    def setUp(self):
        # Create Enterprise user
        self.enterprise_user = User.objects.create_user(
            username='enterprise_user',
            password='TestPass123!'
        )
        UserProfile.objects.create(user=self.enterprise_user, role='ENTERPRISE')
        
        # Create Manager user
        self.manager_user = User.objects.create_user(
            username='manager_user',
            first_name='John',
            last_name='Doe',
            password='TestPass123!'
        )
        UserProfile.objects.create(
            user=self.manager_user,
            role='MANAGER',
            staff_id='MGR001',
            department='IT'
        )
        
        # Create Employee user
        self.employee_user = User.objects.create_user(
            username='employee_user',
            first_name='Jane',
            last_name='Smith',
            password='TestPass123!'
        )
        UserProfile.objects.create(
            user=self.employee_user,
            role='EMPLOYEE',
            staff_id='EMP001',
            department='HR'
        )
        
        self.client = Client()
        self.login_url = reverse('accounts:login')
    
    def test_enterprise_user_cannot_login_as_manager(self):
        """Enterprise user should not be able to login through manager tab"""
        response = self.client.post(self.login_url, {
            'username': 'enterprise_user',
            'password': 'TestPass123!',
            'login_type': 'manager'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This account is registered as Enterprise')
    
    def test_manager_user_cannot_login_as_enterprise(self):
        """Manager should not be able to login through enterprise tab"""
        response = self.client.post(self.login_url, {
            'username': 'manager_user',
            'password': 'TestPass123!',
            'login_type': 'enterprise'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This account is registered as Manager')
    
    def test_manager_can_login_with_correct_tab(self):
        """Manager should successfully login through manager tab"""
        response = self.client.post(self.login_url, {
            'username': 'manager_user',
            'password': 'TestPass123!',
            'login_type': 'manager'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.profile.role, 'MANAGER')
    
    def test_manager_can_login_with_staff_id(self):
        """Manager should be able to login with staff ID"""
        response = self.client.post(self.login_url, {
            'username': 'MGR001',
            'password': 'TestPass123!',
            'login_type': 'manager'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_employee_cannot_login_as_manager(self):
        """Employee should not be able to login through manager tab"""
        response = self.client.post(self.login_url, {
            'username': 'employee_user',
            'password': 'TestPass123!',
            'login_type': 'manager'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This account is registered as Employee')
