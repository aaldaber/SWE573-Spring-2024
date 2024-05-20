import json
from django.test import TestCase
from .models import User, Community, PostTemplate
from django.urls import reverse


def create_user(email, password):
    user = User.objects.create_user(email=email, password=password)
    return user


class CommunityTest(TestCase):
    password = "comm_pass_$123"
    email = "community_user@local.local"

    def test_new_community(self):
        user = create_user(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        self.assertEqual(Community.objects.all()[0].name, "community")
        self.assertEqual(Community.objects.all()[0].owner.email, self.email)
        # check adding another community with the same name
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        self.assertEqual(Community.objects.all().count(), 1)

    def test_edit_community(self):
        user = create_user(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        the_community = Community.objects.all()[0]
        response = self.client.post(reverse("community_edit", args=(the_community.id,)),
                                    {"name": "community_edited", "description": "description_edited",
                                                                  "is_public": "false"})
        self.assertEqual(Community.objects.all()[0].name, "community_edited")
        self.assertEqual(Community.objects.all()[0].is_public, False)

    def test_new_community_default_template_created(self):
        user = create_user(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        the_community = Community.objects.all()[0]
        self.assertEqual(the_community.name, "community")
        self.assertEqual(the_community.post_templates.count(), 1)
        self.assertEqual(the_community.post_templates.all()[0].name, "Default template")

    def test_create_custom_template(self):
        template_payload = '{"payload": {"values":["text field","text area","integer field","float field","boolean field","date field","datetime field","file field","image field","geolocation field"],"reqs":[true,false,true,false,false,false,false,true,false,true],"theorder":["text","textarea","integer","float","boolean","date","datetime","file","image","geolocation"],"template_name":"Custom template"}}'
        user = create_user(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(reverse("community_create"), {"name": "community", "description": "description",
                                                                  "is_public": "true"})
        the_community = Community.objects.all()[0]
        self.assertEqual(the_community.name, "community")
        response = self.client.post(reverse("community_templates_create", args=(the_community.id,)),
                                    data=json.loads(template_payload), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(the_community.post_templates.count(), 2)
        self.assertEqual(the_community.post_templates.all()[1].name, "Custom template")

