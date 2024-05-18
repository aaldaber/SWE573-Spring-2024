from django.apps import AppConfig
from watson import search


class CommunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'community'

    def ready(self):
        Community = self.get_model("Community")
        search.register(Community, fields=("name", "description",))
