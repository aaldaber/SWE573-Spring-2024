from django.shortcuts import render
from .models import Community, Post
from django.http import HttpResponse, Http404
from django.db.models import Q


def index(request):
    latest_posts_in_communities = Post.objects.filter(Q(community__followers=request.user) |
                                                      Q(community__moderators=request.user) |
                                                      Q(community__owner=request.user)).order_by('-date_created')
    list_of_public_communities = Community.objects.filter(is_public=True)
    return render(request, 'community/index.html', {'posts': latest_posts_in_communities})


def post_detail(request, commid, postid):
    try:
        post = Post.objects.get(pk=postid, community__id=commid)
    except Post.DoesNotExist:
        raise Http404
    return render(request, 'community/post_detail.html', {'content': post.get_html_content()})


def community_create(request):
    pass


def community_list(request):
    communities = Community.objects.all()
    return render(request, 'community/community_list.html', {'community_list': communities})


def community_templates_list(request, commid):
    try:
        community = Community.objects.get(pk=commid)
    except Community.DoesNotExist:
        raise Http404

    return render(request, 'community/template_list.html', {'template_list': community.post_templates.all()})