import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.template import engines

User = get_user_model()
django_engine = engines['django']


class Community(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_communities')
    moderators = models.ManyToManyField(User, related_name='moderated_communities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"


class PostTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='post_templates')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Post Template"
        verbose_name_plural = "Post Templates"
        unique_together = ("community", "name",)


class Field(models.Model):
    data_type = models.CharField(max_length=100, unique=True)
    html_content = models.TextField()

    def __str__(self):
        return self.data_type

    class Meta:
        verbose_name = "Field"
        verbose_name_plural = "Fields"


class TemplateField(models.Model):
    template = models.ForeignKey(PostTemplate, on_delete=models.CASCADE, related_name='fields')
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.template.name} - {self.label}"

    class Meta:
        verbose_name = "Template Field"
        verbose_name_plural = "Template Fields"


class Post(models.Model):
    title = models.CharField(max_length=255)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    template = models.ForeignKey(PostTemplate, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author.username}'s post in {self.community.name}"

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
    content_text = models.TextField(blank=True, null=True)
    content_file = models.FileField(upload_to='post_files/', blank=True, null=True)

    def __str__(self):
        return f"{self.post} - {self.template_field.label}"

    def get_content(self):
        if self.content_text:
            return self.content_text
        elif self.content_file:
            return self.content_file.url
        else:
            return ""

    def get_html_content(self):
        template = django_engine.from_string(self.template_field.field.html_content)
        if self.content_text:
            return template.render({"content": self.content_text}, request=None)
        else:
            return template.render({"content": self.content_file.url}, request=None)

    class Meta:
        verbose_name = "Post Field"
        verbose_name_plural = "Post Fields"