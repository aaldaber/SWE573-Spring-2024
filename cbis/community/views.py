import json
from django.contrib import messages
from django.shortcuts import render
from .models import Community, Post, PostTemplate, TemplateField, PostField
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.urls import reverse
from .forms import CreateCommunityForm, TemplateForm, TemplatePreviewForm, PostForm, TemplateSearchForm
from .signals import post_viewed
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from watson import search


@login_required
def index(request):
    latest_posts_in_communities = Post.objects.filter(Q(community__followers=request.user) |
                                                      Q(community__moderators=request.user) |
                                                      Q(community__owner=request.user) |
                                                      Q(community__is_public=True)).order_by('-date_created')[:10]
    one_day_ago = timezone.now() - timezone.timedelta(hours=24)
    most_viewed_posts_today = Post.objects.filter((Q(community__followers=request.user) |
                                                      Q(community__moderators=request.user) |
                                                      Q(community__owner=request.user) |
                                                      Q(community__is_public=True)) & (Q(postviews__view_date__gte=one_day_ago) & Q(postviews__view_date__lte=timezone.now()))).annotate(views=Count("postviews", filter=Q(postviews__view_date__gte=one_day_ago) & Q(postviews__view_date__lte=timezone.now()))).order_by('-views', '-date_created')[:10]
    most_viewed_posts_all_time = Post.objects.filter(Q(community__followers=request.user) |
                                                      Q(community__moderators=request.user) |
                                                      Q(community__owner=request.user) |
                                                      Q(community__is_public=True)).order_by('-view_count', '-date_created')[:10]
    return render(request, 'community/index.html', {'latest_posts': latest_posts_in_communities,
                                                    'most_viewed_today': most_viewed_posts_today,
                                                    'most_viewed_all': most_viewed_posts_all_time})


@login_required
def post_detail(request, commid, postid):
    try:
        community = Community.objects.get(pk=commid)
        if community.is_public or community.followers.filter(id=request.user.id).exists() or \
                community.moderators.filter(id=request.user.id).exists() or \
                community.owner == request.user:
            post = Post.objects.get(pk=postid, community=community)
            post_viewed.send(sender=None, instance=post, request=request)
        else:
            return HttpResponseForbidden()
    except Post.DoesNotExist:
        raise Http404
    except Community.DoesNotExist:
        raise Http404
    return render(request, 'community/post_detail.html', {'content': post.get_html_content(),
                                                          'post': post})


@login_required
def community_create(request):
    if request.method == 'GET':
        create_form = CreateCommunityForm()
        return render(request, 'community/community_create.html', {'form': create_form})
    elif request.method == 'POST':
        create_form = CreateCommunityForm(request.POST, files=request.FILES)
        if create_form.is_valid():
            community = create_form.save(commit=False)
            community.owner = request.user
            community.save()
            # adding a default template
            template = PostTemplate(community=community, name="Default template", created_by=request.user)
            template.save()
            TemplateField(template=template, data_type=TemplateField.TEXTAREA, label="Post text", required=True).save()
            return HttpResponseRedirect(reverse("community_list"))
        else:
            messages.warning(request, "Please fix the form errors")
            return render(request, 'community/community_create.html', {'form': create_form})


@login_required
def community_edit(request, commid):
    try:
        community = Community.objects.get(pk=commid)
    except Community.DoesNotExist:
        raise Http404
    if not community.moderators.filter(id=request.user.id).exists() and \
            not community.owner == request.user:
        return HttpResponseForbidden()
    if request.method == 'GET':
        create_form = CreateCommunityForm(instance=community)
        return render(request, 'community/community_edit.html', {'form': create_form, 'community': community})
    elif request.method == 'POST':
        create_form = CreateCommunityForm(instance=community, data=request.POST, files=request.FILES)
        if create_form.is_valid():
            community = create_form.save()
            community.save()
            return HttpResponseRedirect(reverse("community_detail", args=(community.id,)))
        else:
            messages.warning(request, "Please fix the form errors")
            return render(request, 'community/community_edit.html', {'form': create_form, 'community': community})


@login_required
def community_detail(request, commid):
    try:
        community = Community.objects.get(pk=commid)
        is_member = request.user.followed_communities.filter(id=community.id).exists()
        is_moderator = request.user.moderated_communities.filter(id=community.id).exists()
        is_owner = request.user.owned_communities.filter(id=community.id).exists()
        if not community.is_public and not is_member and \
                not is_moderator and not is_owner:
            posts = community.posts.none()
        else:
            posts = community.posts.all().order_by('-date_created')
    except Community.DoesNotExist:
        raise Http404

    return render(request, 'community/community_detail.html', {'community': community, 'posts': posts,
                                                               'is_member': is_member, 'is_moderator': is_moderator,
                                                               'is_owner': is_owner,
                                                               'templates': community.post_templates.all()})


@login_required
def community_list(request):
    communities = Community.objects.filter(Q(is_public=True) | Q(owner=request.user) | Q(followers=request.user) | Q(moderators=request.user))
    return render(request, 'community/community_list.html', {'community_list': communities})


@login_required
def community_templates_list(request, commid):
    try:
        community = Community.objects.get(pk=commid)
        is_member = request.user.followed_communities.filter(id=community.id).exists()
        is_moderator = request.user.moderated_communities.filter(id=community.id).exists()
        is_owner = request.user.owned_communities.filter(id=community.id).exists()
        if not is_member and not is_moderator and not is_owner:
            return HttpResponseForbidden()
    except Community.DoesNotExist:
        raise Http404

    return render(request, 'community/template_list.html', {'template_list': community.post_templates.all().order_by('date_created'),
                                                            'community': community,
                                                            'is_member': is_member,
                                                            'is_moderator': is_moderator,
                                                            'is_owner': is_owner})


def validate_template_json(data, community, user, create_or_edit, template=None):
    data_types = [x[0] for x in TemplateField.TYPE_CHOICES]
    if not data["template_name"].replace(' ', '').isalnum() or len(data["template_name"].replace(' ', '')) < 5:
        return JsonResponse({"error": "Template name should be alphanumeric and at least 5 characters in length"},
                            status=400)
    if create_or_edit == "create":
        if PostTemplate.objects.filter(name=data["template_name"], community=community).exists():
            return JsonResponse({"error": "Template with the same name already exists"}, status=400)
    elif create_or_edit == "edit":
        if PostTemplate.objects.filter(name=data["template_name"], community=community).exclude(
                id=template.id).exists():
            return JsonResponse({"error": "Template with the same name already exists"}, status=400)
    for each in data["reqs"]:
        if type(each) is not bool:
            return JsonResponse({"error": "Required type should be boolean"}, status=400)
    if not all([x.replace(' ', '').isalnum() for x in data["values"]]):
        return JsonResponse({"error": "Labels should be alpanumeric"}, status=400)
    if len(data["values"]) != len(set(data["values"])):
        return JsonResponse({"error": "Labels should be unique"}, status=400)
    for each in data["theorder"]:
        if each not in data_types:
            return JsonResponse({"error": "Data type {} does not exists in our system".format(each)}, status=400)
    if create_or_edit == "create":
        new_template = PostTemplate(name=data["template_name"], community=community, created_by=user)
        new_template.save()
        count = 0
        for each in data["theorder"]:
            TemplateField(template=new_template, data_type=each, order=count, label=data["values"][count],
                          required=data["reqs"][count]).save()
            count += 1
        return JsonResponse({"template": new_template.id})
    elif create_or_edit == "edit":
        template.name = data["template_name"]
        template.save()
        template.fields.all().delete()
        count = 0
        for each in data["theorder"]:
            TemplateField(template=template, data_type=each, order=count, label=data["values"][count],
                          required=data["reqs"][count]).save()
            count += 1
        return JsonResponse({"template": template.id})


@login_required
def community_templates_create(request, commid):
    try:
        community = Community.objects.get(pk=commid)
    except Community.DoesNotExist:
        raise Http404
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'GET':
        form = TemplateForm()
        return render(request, 'community/template_create.html', {'form': form,
                                                                  'community': community})
    elif request.method == 'POST' and is_ajax:
        try:
            data = json.load(request)['payload']
            return validate_template_json(data, community, request.user, "create")
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": "Request error, please check your data"}, status=400)


@login_required
def community_templates_edit(request, commid, template_id):
    try:
        community = Community.objects.get(pk=commid)
        template = PostTemplate.objects.get(pk=template_id, community=community)
    except Community.DoesNotExist:
        raise Http404
    except PostTemplate.DoesNotExist:
        raise Http404
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'GET':
        if template.posts.count():
            return render(request, 'community/template_edit_forbidden.html', {'posts': template.posts.all()})
        else:
            form = TemplateForm(initial={"name": template.name})
            return render(request, 'community/template_edit.html', {'form': form,
                                                                  'community': community,
                                                                  'template': template,
                                                                  'template_fields': template.fields.all().order_by('order'),
                                                                })
    elif request.method == 'POST' and is_ajax:
        if template.posts.count():
            return JsonResponse({"error": "You cannot edit a template that has associated posts"},
                                status=400)
        try:
            data = json.load(request)['payload']
            return validate_template_json(data, community, request.user, "edit", template)
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": "Request error, please check your data"}, status=400)


@login_required
def community_templates_preview(request, commid, template_id):
    try:
        community = Community.objects.get(pk=commid)
        template = PostTemplate.objects.get(pk=template_id, community=community)
    except Community.DoesNotExist:
        raise Http404
    except PostTemplate.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        form = TemplatePreviewForm(fields=template.fields.all().order_by('order'))
        return render(request, 'community/template_preview.html', {'form': form, 'template': template})


@login_required
def community_template_search(request, commid, template_id):
    try:
        community = Community.objects.get(pk=commid)
        template = PostTemplate.objects.get(pk=template_id, community=community)
    except Community.DoesNotExist:
        raise Http404
    except PostTemplate.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        form = TemplateSearchForm(fields=template.fields.all().order_by('order'))
        return render(request, 'community/template_search.html', {'form': form, 'template': template})
    elif request.method == 'POST':
        form = TemplateSearchForm(fields=template.fields.all().order_by('order'), data=request.POST)
        if form.is_valid():
            range_filters = {}
            all_posts = set()
            main_queryset = PostField.objects.filter(template_field__template=template, post__community=community)
            title = form.cleaned_data.pop('post_title', None)
            if title:
                community_queryset = Post.objects.filter(community=community, template=template)
                posts = search.filter(community_queryset, title)
                all_posts.update(posts.values_list('id', flat=True))
            for eachname, eachvalue in form.cleaned_data.items():
                if eachvalue:
                    if not eachname.endswith("_to") and not eachname.endswith("_from"):
                        if (template.fields.get(label=eachname).data_type == TemplateField.TEXT or
                                template.fields.get(label=eachname).data_type == TemplateField.TEXTAREA):
                            text_queryset = search.filter(main_queryset, eachvalue)
                            print("text_queryset", text_queryset)
                            all_posts.update(text_queryset.values_list('post__id', flat=True))
                    else:
                        field_name = eachname.replace("_to", "").replace("_from", "")
                        field_type = template.fields.get(label=field_name).data_type
                        if (field_type == TemplateField.INTEGER or
                            field_type == TemplateField.FLOAT or
                            field_type == TemplateField.DATETIME or
                            field_type == TemplateField.DATE):
                            if eachname.endswith("_from"):
                                range_filters["content_{}".format(field_type)+"__gte"] = eachvalue
                            elif eachname.endswith("_to"):
                                range_filters["content_{}".format(field_type)+"__lte"] = eachvalue
            if range_filters:
                range_queryset = main_queryset.filter(**range_filters)
                all_posts.update(range_queryset.values_list('post__id', flat=True))
            posts = Post.objects.filter(id__in=list(all_posts))
            return render(request, 'community/template_search.html', {'form': form, 'posts': posts,
                                                                  'template': template, 'community': community})
        else:
            form = TemplateSearchForm(fields=template.fields.all().order_by('order'), data=request.POST)
            return render(request, 'community/template_search.html', {'form': form, 'template': template})


@login_required
def community_new_post(request, commid, template_id):
    try:
        community = Community.objects.get(pk=commid)
        template = PostTemplate.objects.get(pk=template_id, community=community)
    except Community.DoesNotExist:
        raise Http404
    except PostTemplate.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        form1 = PostForm()
        form = TemplatePreviewForm(fields=template.fields.all().order_by('order'))
        return render(request, 'community/new_post.html', {'form': form,
                                                           'form1': form1,
                                                           'template': template,
                                                           'community': community})
    elif request.method == 'POST':
        form = TemplatePreviewForm(fields=template.fields.all().order_by('order'), data=request.POST, files=request.FILES)
        form1 = PostForm(data=request.POST)
        if form.is_valid() and form1.is_valid():
            new_post = Post(title=form1.cleaned_data['post_title'], community=community, template=template,
                            author=request.user)
            new_post.save()
            for each in template.fields.all().order_by('order'):
                if form.cleaned_data.get(each.label):
                    post_field = PostField(post=new_post, template_field=each)
                    if each.data_type == "geolocation":
                        setattr(post_field, "content_{}".format(each.data_type), [form.cleaned_data.get(each.label).y, form.cleaned_data.get(each.label).x])
                    else:
                        setattr(post_field, "content_{}".format(each.data_type), form.cleaned_data.get(each.label))
                    post_field.save()
            return HttpResponseRedirect(reverse("postdetail", args=(community.id, new_post.id,)))
        else:
            errors = ''
            if form.errors:
                errors += str(form.errors)
            if form1.errors:
                errors += str(form1.errors)
            messages.warning(request, mark_safe(errors))
            return render(request, 'community/new_post.html', {'form': form,
                                                               'form1': form1,
                                                               'template': template,
                                                               'community': community})


@login_required
def join_community(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST' and is_ajax:
        try:
            data = json.load(request)['payload']
            community = Community.objects.get(pk=data['commid'])
            if community.is_public:
                community.followers.add(request.user)
                return JsonResponse({"message": "success"})
            else:
                messages.success(request, "Your request to join this community has been received by our moderators.")
                return JsonResponse({"message": "success"})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": "Request error, please check your data"}, status=400)


@login_required
def community_search(request):
    if request.method == 'GET':
        query = request.GET.get("q")
        if not query or len(query) < 3:
            results = []
        else:
            results = search.filter(Community, query)
        return render(request, "community/search_results_communities.html", {"community_list": results})
