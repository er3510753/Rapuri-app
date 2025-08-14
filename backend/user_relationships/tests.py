from django.test import TestCase
from .models import UserRelationship
from django.contrib.auth import get_user_model

class UserRelationshipModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')

    def test_create_relationship(self):
        rel = UserRelationship.objects.create(
            follower=self.user1,
            followed=self.user2,
            status=UserRelationship.STATUS_PENDING
        )
        self.assertEqual(rel.follower, self.user1)
        self.assertEqual(rel.followed, self.user2)
        self.assertEqual(rel.status, UserRelationship.STATUS_PENDING)

    def test_relationship_str(self):
        rel = UserRelationship.objects.create(
            follower=self.user1,
            followed=self.user2,
            status=UserRelationship.STATUS_APPROVED
        )
        self.assertIn('user1', str(rel))
        self.assertIn('user2', str(rel))
        self.assertIn('承認済み', str(rel))
