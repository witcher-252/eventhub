from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_organizer)

    def test_create_organizer(self):
        organizer = User.objects.create_user(username="organizeruser", password="testpass123", is_organizer=True)
        self.assertTrue(organizer.is_organizer)
