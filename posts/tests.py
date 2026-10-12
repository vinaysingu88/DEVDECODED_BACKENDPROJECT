
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Posts

User = get_user_model()


class PostModerationTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            name='Test Author',
            email='author@example.com',
            password='TestPassword123!'
        )

        self.post = Posts.objects.create(
            title='Original title',
            content='Original content',
            author=self.author,
            status='APPROVED'
        )

        token = str(RefreshToken.for_user(self.author).access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

    def test_author_edit_resets_status_to_pending(self):
        response = self.client.put(
            f'/api/posts/{self.post.id}/',
            {
                'title': 'Updated title',
                'content': 'Updated content'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'PENDING')
        self.assertEqual(self.post.title, 'Updated title')
