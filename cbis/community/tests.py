from django.test import TestCase
from .models import User, Community
from django.urls import reverse


def create_user(email, password):
    user = User.objects.create_user(email=email, password=password)
    return user


class CommunityTest(TestCase):
    def test_new_community(self):
        user_password = "comm_pass_$123"
        email = "community_user@local.local"
        user = create_user(email=email, password=user_password)
        self.client.login(email=email, password=user_password)
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        self.assertEqual(Community.objects.all()[0].name, "community")
        self.assertEqual(Community.objects.all()[0].owner.email, email)
        # check adding another community with the same name
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        self.assertEqual(Community.objects.all().count(), 1)

    def test_edit_community(self):
        user_password = "comm_pass_$123"
        email = "community_user@local.local"
        user = create_user(email=email, password=user_password)
        self.client.login(email=email, password=user_password)
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        the_community = Community.objects.all()[0]
        response = self.client.post(reverse("community_edit", args=(the_community.id,)),
                                    {"name": "community_edited", "description": "description_edited",
                                                                  "is_public": "false"})
        self.assertEqual(Community.objects.all()[0].name, "community_edited")
        self.assertEqual(Community.objects.all()[0].is_public, False)

