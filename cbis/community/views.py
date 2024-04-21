from django.shortcuts import render
from .models import Community
from django.http import HttpResponse, Http404


def community_list(request):
    community_list = Community.objects.all()
    return render(request, 'community/community_list.html', {'community_list': community_list})


def community_templates_list(request, commid):
    try:
        community = Community.objects.get(pk=commid)
    except Community.DoesNotExist:
        return Http404

    return render(request, 'community/template_list.html', {'template_list': community.post_templates.all()})