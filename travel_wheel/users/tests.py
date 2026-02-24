from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTest(TestCase):

    def test_user_creation(self):
        user = User.objects.create_user(
            username="test",
            password="123456"
        )
        self.assertTrue(user.check_password("123456"))