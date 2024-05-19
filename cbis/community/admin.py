from django.contrib import admin
from .models import Community, Post, TemplateField, PostField, PostTemplate, JoinRequest


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'community', 'author', 'date_created', 'date_edited']


admin.site.register(Community)
admin.site.register(Post, PostAdmin)
admin.site.register(TemplateField)
admin.site.register(PostField)
admin.site.register(PostTemplate)
admin.site.register(JoinRequest)
