from django.contrib import admin
from .models import Community, Post, TemplateField, PostField, PostTemplate
from django.utils.html import format_html


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'community', 'author', 'date_created', 'date_edited']

    readonly_fields = ('html_representation',)

    def html_representation(self, obj):
        return format_html(obj.get_html_content())


admin.site.register(Community)
admin.site.register(Post, PostAdmin)
admin.site.register(TemplateField)
admin.site.register(PostField)
admin.site.register(PostTemplate)
