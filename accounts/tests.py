from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse


class AdminUsersPageTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.admin_group = Group.objects.create(
            name="Admin"
        )

        cls.inspector_group = Group.objects.create(
            name="Inspector"
        )

        cls.admin_user = User.objects.create_user(
            username="test_admin",
            password="TestPassword123"
        )

        cls.admin_user.groups.add(
            cls.admin_group
        )

        cls.inspector_user = User.objects.create_user(
            username="test_inspector",
            password="TestPassword123"
        )

        cls.inspector_user.groups.add(
            cls.inspector_group
        )


    def test_admin_can_access_admin_users_page(self):

        self.client.login(
            username="test_admin",
            password="TestPassword123"
        )

        response = self.client.get(
            reverse("admin-users")
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_inspector_cannot_access_admin_users_page(self):

        self.client.login(
            username="test_inspector",
            password="TestPassword123"
        )

        response = self.client.get(
            reverse("admin-users")
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            response.url,
            reverse("dashboard")
        )


class BrowserAuthenticationTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(
            username="test_login",
            password="TestPassword123"
        )


    def test_valid_user_can_login(self):

        response = self.client.post(
            reverse("login"),
            {
                "username": "test_login",
                "password": "TestPassword123",
            }
        )

        self.assertRedirects(
            response,
            reverse("dashboard")
        )

        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )


    def test_invalid_credentials_are_rejected(self):

        response = self.client.post(
            reverse("login"),
            {
                "username": "test_login",
                "password": "WrongPassword123",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )


    def test_logged_in_user_can_logout(self):

        self.client.login(
            username="test_login",
            password="TestPassword123"
        )

        response = self.client.get(
            reverse("logout")
        )

        self.assertRedirects(
            response,
            reverse("login")
        )

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}"
        )