import os
import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.template import engines
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from .signals import post_viewed
from django.db.models import F

User = get_user_model()
django_engine = engines['django']


def community_photo_upload(self, filename):
    extension = filename.split('.')[-1]
    filename = 'community_{}.{}'.format(self.id, extension)
    return os.path.join('community_photos/', filename)


class Community(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_communities')
    moderators = models.ManyToManyField(User, blank=True, related_name='moderated_communities')
    followers = models.ManyToManyField(User, blank=True, related_name='followed_communities')
    picture = models.ImageField(upload_to=community_photo_upload, blank=True, null=True)

    @property
    def follower_count(self):
        return self.followers.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"


class PostTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='post_templates')
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Post Template"
        verbose_name_plural = "Post Templates"
        unique_together = ("community", "name",)


class TemplateField(models.Model):
    TEXT = "text"
    TEXTAREA = "textarea"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    FILE = "file"
    IMAGE = "image"
    GEOLOCATION = "geolocation"

    TYPE_CHOICES = (
        (TEXT, "Text"),
        (TEXTAREA, "Text Area"),
        (INTEGER, "Integer"),
        (BOOLEAN, "True / False"),
        (FLOAT, "Float"),
        (DATE, "Date"),
        (DATETIME, "Datetime"),
        (FILE, "File"),
        (IMAGE, "Image"),
        (GEOLOCATION, "Geolocation")
    )
    template = models.ForeignKey(PostTemplate, on_delete=models.CASCADE, related_name='fields')
    data_type = models.CharField(choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0], max_length=100)
    label = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.template.name} - {self.label}"

    def generate_html_template_edit(self):
        return '<div data-id="{}" class="list-group-item nested-1"><a href="#" class="remove_field">Remove</a><br><label>Label:</label><input type="text" class="label" value="{}"><br><label>Required:</label><input type="checkbox" class="chkbx" {}><br><b><i>{}</i></b></div>'.format(self.data_type, self.label, "checked" if self.required else '', dict(self.TYPE_CHOICES).get(self.data_type))

    class Meta:
        verbose_name = "Template Field"
        verbose_name_plural = "Template Fields"


class Post(models.Model):
    title = models.CharField(max_length=255)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    template = models.ForeignKey(PostTemplate, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    view_count = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.title} in {self.community.name}"

    def get_html_content(self):
        full_html = ''
        for each in self.fields.all().order_by('template_field__order'):
            template = django_engine.from_string("<div>{{label}}: {{content}}</div>")
            full_html += template.render({"label": each.template_field.label, "content": each.get_html_content()},
                                         request=None)
        return full_html

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"


class PostField(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='fields')
    template_field = models.ForeignKey(TemplateField, on_delete=models.CASCADE, related_name='post_fields')
    content_text = models.CharField(max_length=255, blank=True, null=True)
    content_textarea = models.TextField(blank=True, null=True)
    content_integer = models.IntegerField(blank=True, null=True)
    content_boolean = models.BooleanField(blank=True, null=True)
    content_float = models.FloatField(blank=True, null=True)
    content_image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    content_file = models.FileField(upload_to='post_files/', blank=True, null=True)
    content_date = models.DateField(blank=True, null=True)
    content_datetime = models.DateTimeField(blank=True, null=True)
    content_geolocation = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.post} - {self.template_field.label}"

    def get_html_content(self):
        if self.template_field.data_type == TemplateField.TEXT:
            template = "{{ content }}"
            data = self.content_text
        elif self.template_field.data_type == TemplateField.IMAGE:
            template = '<img src="{{content}}" class="img-fluid" />'
            data = self.content_image.url
        elif self.template_field.data_type == TemplateField.FILE:
            template = '<a href="{{content}}"/>File</a>'
            data = self.content_file.url
        elif self.template_field.data_type == TemplateField.INTEGER:
            template = "{{ content }}"
            data = self.content_integer
        elif self.template_field.data_type == TemplateField.BOOLEAN:
            template = "{{ content }}"
            data = "True" if self.content_boolean else "False"
        elif self.template_field.data_type == TemplateField.FLOAT:
            template = "{{ content }}"
            data = self.content_float
        elif self.template_field.data_type == TemplateField.TEXTAREA:
            template = "<p>{{ content }} </p>"
            data = self.content_textarea
        elif self.template_field.data_type == TemplateField.DATE:
            template = "{{ content }}"
            data = self.content_date
        elif self.template_field.data_type == TemplateField.DATETIME:
            template = "{{ content }}"
            data = self.content_datetime
        elif self.template_field.data_type == TemplateField.GEOLOCATION:
            template = ('{% load leaflet_tags %}'
                        '<script>'
                        'function map_init_basic_' + str(self.id) +
                        ' (map, options) {'
                        'L.marker({{content}}).addTo(map); map.setView({{content}}, 10);'
                        '}'
                        '</script>'
                        '{% leaflet_map "') + "map_{}".format(self.id) + '" callback="window.map_init_basic_' + str(self.id) + '" %}'
            data = str(self.content_geolocation)
        template = django_engine.from_string(template)
        return template.render({"content": data}, request=None)

    class Meta:
        verbose_name = "Post Field"
        verbose_name_plural = "Post Fields"


class PostViews(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="viewedposts")
    view_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Post View"
        verbose_name_plural = "Post Views"
        unique_together = ('post', 'user', )


class JoinRequest(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    request_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Join Request"
        verbose_name_plural = "Join Requests"
        unique_together = ('community', 'user',)


@receiver(post_viewed)
def update_post_count(sender, instance, request, **kwargs):
    if request.user.is_authenticated:
        if not PostViews.objects.filter(post=instance, user=request.user).exists():
            PostViews(post=instance, user=request.user).save()
            instance.view_count = F("view_count") + 1
            instance.save(update_fields=["view_count"])
