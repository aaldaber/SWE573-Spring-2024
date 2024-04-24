from django.contrib import messages
from django.shortcuts import render
from .models import Community, Post, PostTemplate, TemplateField
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from .formsets import TemplateFieldFormSet
from .forms import CreateCommunityForm


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
    return render(request, 'community/post_detail.html', {'content': post.get_html_content(),
                                                          'post': post})


def community_create(request):
    if request.method == 'GET':
        create_form = CreateCommunityForm()
        return render(request, 'community/community_create.html', {'form': create_form})
    elif request.method == 'POST':
        create_form = CreateCommunityForm(request.POST)
        if create_form.is_valid():
            community = create_form.save(commit=False)
            community.owner = request.user
            community.save()
            return HttpResponseRedirect(reverse("community_list"))
        else:
            messages.warning(request, "Please fix the form errors")
            return render(request, 'community/community_create.html', {'form': create_form})


def community_detail(request, commid):
    try:
        community = Community.objects.get(pk=commid)
        posts = community.posts.all().order_by('-date_created')
    except Community.DoesNotExist:
        raise Http404

    return render(request, 'community/community_detail.html', {'community': community, 'posts': posts})


def community_list(request):
    communities = Community.objects.all()
    return render(request, 'community/community_list.html', {'community_list': communities})


def community_templates_list(request, commid):
    try:
        community = Community.objects.get(pk=commid)
    except Community.DoesNotExist:
        raise Http404

    return render(request, 'community/template_list.html', {'template_list': community.post_templates.all()})


def community_templates_create(request, commid):
    community = Community.objects.get(pk=commid)
    template = PostTemplate()

    formset = TemplateFieldFormSet()
