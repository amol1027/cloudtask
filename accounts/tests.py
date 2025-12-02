from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile

class RegistrationLoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.dashboard_url = reverse('dashboard:index')

    def test_registration_creates_enterprise_user(self):
        """Test that registration creates a user with ENTERPRISE role and redirects to login"""
        response = self.client.post(self.register_url, {
            'username': 'newenterprise',
            'password1': 'StrongPass123!', 
            'password2': 'StrongPass123!'
        })
        
        # If form is invalid, response code will be 200 (re-render form).
        # If valid, it redirects (302).
        if response.status_code == 200:
            print(response.context['form'].errors)
            
        self.assertRedirects(response, self.login_url)
        
        # Check user created
        user = User.objects.get(username='newenterprise')
        
        # Check profile created with correct role
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'ENTERPRISE')

    def test_login_redirects_to_dashboard(self):
        """Test that login redirects to dashboard"""
        # Create a user first
        user = User.objects.create_user(username='existinguser', password='password123')
        UserProfile.objects.create(user=user, role='ENTERPRISE')
        
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'password123'
        })
        
        # Check redirect to dashboard
        self.assertRedirects(response, self.dashboard_url)
