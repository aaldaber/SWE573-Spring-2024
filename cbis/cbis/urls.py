"""
URL configuration for cbis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from community import views as comm_views
from user import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', user_views.signup, name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("", comm_views.index, name="index"),
    path("join-community", comm_views.join_community, name="join-community"),
    path("profile-edit/", user_views.profile_edit, name="profile-edit"),
    path("communities/", comm_views.community_list, name="community_list"),
    path("communities/create/", comm_views.community_create, name="community_create"),
    path("communities/<uuid:commid>/", comm_views.community_detail, name="community_detail"),
    path("communities/<uuid:commid>/edit/", comm_views.community_edit, name="community_edit"),
    path("communities/<uuid:commid>/templates/", comm_views.community_templates_list, name="community_templates_list"),
    path("communities/<uuid:commid>/templates/create/", comm_views.community_templates_create, name="community_templates_create"),
    path("communities/<uuid:commid>/templates/edit/<uuid:template_id>/", comm_views.community_templates_edit, name="community_templates_edit"),
    path("communities/<uuid:commid>/templates/preview/<uuid:template_id>/", comm_views.community_templates_preview, name="community_templates_preview"),
    path("communities/<uuid:commid>/templates/search/<uuid:template_id>/", comm_views.community_template_search, name="community_template_search"),
    path("communities/<uuid:commid>/create-post/<uuid:template_id>/", comm_views.community_new_post, name="community_new_post"),
    path("communities/<uuid:commid>/<int:postid>/", comm_views.post_detail, name="postdetail"),
    path("search/community/", comm_views.community_search, name="community_search")
]
