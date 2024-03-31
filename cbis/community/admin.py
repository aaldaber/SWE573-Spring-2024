from django.contrib import admin
from .models import Community, Post, TemplateField, PostField, PostTemplate, Field

admin.site.register(Community)
admin.site.register(Post)
admin.site.register(TemplateField)
admin.site.register(PostField)
admin.site.register(PostTemplate)
admin.site.register(Field)

