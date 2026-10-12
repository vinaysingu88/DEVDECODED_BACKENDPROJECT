
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserAPITests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(
            name="Test Author",
            email="author@example.com",
            password="TestPassword123!"
        )

        self.admin = User.objects.create_superuser(
            name="Test Admin",
            email="admin@example.com",
            password="AdminPassword123!"
        )

        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.admin_users_url = "/api/admin/users/"

    def authenticate_as(self, user):
        access_token = str(
            RefreshToken.for_user(user).access_token
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    def test_register_author(self):
        response = self.client.post(
            self.register_url,
            {
                "name": "New Author",
                "email": "newauthor@example.com",
                "password": "NewPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = User.objects.get(email="newauthor@example.com")
        self.assertEqual(user.role, "AUTHOR")
        self.assertTrue(user.check_password("NewPassword123!"))

    def test_registration_cannot_create_admin(self):
        response = self.client.post(
            self.register_url,
            {
                "name": "Fake Admin",
                "email": "fakeadmin@example.com",
                "password": "FakePassword123!",
                "role": "ADMIN"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = User.objects.get(email="fakeadmin@example.com")
        self.assertEqual(user.role, "AUTHOR")

    def test_login_returns_jwt_tokens(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "author@example.com",
                "password": "TestPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["role"], "AUTHOR")

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "author@example.com",
                "password": "WrongPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_admin_can_list_users(self):
        self.authenticate_as(self.admin)

        response = self.client.get(self.admin_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        emails = [user["email"] for user in response.data]
        self.assertIn("author@example.com", emails)
        self.assertIn("admin@example.com", emails)

        # User list must not expose password hashes.
        self.assertNotIn("password", response.data[0])

    def test_author_cannot_list_users(self):
        self.authenticate_as(self.author)

        response = self.client.get(self.admin_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_missing_token_cannot_list_users(self):
        self.client.credentials()

        response = self.client.get(self.admin_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_admin_can_promote_author(self):
        self.authenticate_as(self.admin)

        response = self.client.put(
            "/api/admin/users/{}/role/".format(self.author.id),
            {"role": "ADMIN"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.author.refresh_from_db()
        self.assertEqual(self.author.role, "ADMIN")

    def test_admin_cannot_assign_invalid_role(self):
        self.authenticate_as(self.admin)

        response = self.client.put(
            "/api/admin/users/{}/role/".format(self.author.id),
            {"role": "MANAGER"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_admin_cannot_demote_self(self):
        self.authenticate_as(self.admin)

        response = self.client.put(
            "/api/admin/users/{}/role/".format(self.admin.id),
            {"role": "AUTHOR"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.admin.refresh_from_db()
        self.assertEqual(self.admin.role, "ADMIN")
