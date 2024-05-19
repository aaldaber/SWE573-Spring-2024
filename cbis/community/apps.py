from django.apps import AppConfig
from watson import search


class CommunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'community'

    def ready(self):
        Community = self.get_model("Community")
        PostField = self.get_model("PostField")
        Post = self.get_model("Post")
        search.register(Community, fields=("name", "description",))
        search.register(Post, fields=("title",))
        search.register(PostField, fields=("content_text", "content_textarea",))
