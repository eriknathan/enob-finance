from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(email='test@example.com', password='strongpass')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('strongpass'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        user = User.objects.create_superuser(email='admin@example.com', password='adminpass')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='pass')

    def test_email_is_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='pass1234')

    def test_login_with_correct_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'user@example.com',
            'password': 'pass1234',
        })
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_login_with_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'user@example.com',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_page_accessible(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects(self):
        self.client.login(username='user@example.com', password='pass1234')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class RegisterViewTests(TestCase):
    def test_register_creates_user(self):
        self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'password': 'complexpass123',
            'password_confirm': 'complexpass123',
        })
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_register_with_mismatched_passwords(self):
        self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'password': 'complexpass123',
            'password_confirm': 'differentpass',
        })
        self.assertFalse(User.objects.filter(email='new@example.com').exists())

    def test_register_with_duplicate_email(self):
        User.objects.create_user(email='existing@example.com', password='pass1234')
        response = self.client.post(reverse('register'), {
            'email': 'existing@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 1)
