from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render_to_response
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import Content, Tag, Check

# Create your views here.
@login_required
def index(request):
    all_contents = Content.objects.all().order_by('title')

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(all_contents, 10, request=request)
    contents = p.page(page)
    context = {
        'contents': contents,
        'no_contents': not bool(contents)
    }
    return render(request, 'cms/index.html', context)

@login_required
def watch(request, content_id):
    return render_content(content_id, 'cms/watch_html5.html', request)

@login_required
def watch_flash(request, content_id):
    return render_content(content_id, 'cms/watch_flash.html', request)

@login_required
def watch_jw(request, content_id):
    return render_content(content_id, 'cms/watch_jw.html', request)

def render_content(content_id, template, request):
    content = get_object_or_404(Content, pk=content_id)
    context = {'content': content}
    return render(request, template, context)

@login_required
def tagged_contents(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    all_contents = Content.objects.filter(tags__id__exact=tag.id).order_by('title')

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    p = Paginator(all_contents, 10, request=request)
    contents = p.page(page)

    context = {'contents': contents, 'tag': tag}
    return render(request, 'cms/tagged_contents.html', context)

@login_required
def register_from_file(request):
    if not request.user.is_staff:
        messages.add_message(request, messages.INFO, '権限がありません。')
        return redirect('/')

    if request.method == 'POST':
        items = request.POST
        if 'tags' not in items:
            messages.add_message(request, messages.INFO, 'タグを選択してください。')
            return redirect('cms:register_file')
        context = {'tags': items['tags'], 'text_contents': items['contents']}
        context = parse_text_contents(context)
        messages.add_message(request, messages.INFO, '{}個のコンテンツを追加しました。'.format(len(context['contents'])))
        return redirect('/')

    else: # GET
        tags = Tag.objects.all()
        context = {'tags': tags}
        return render(request, 'cms/register_from_file.html', context)

def parse_text_contents(context):
    title = ''
    contents = []
    tags = Tag.objects.filter(pk__in=context['tags'])
    tags = list(tags)
    for line in context['text_contents'].split('\n'):
        line = line.strip()
        if title:
            url = 'https://s3-ap-northeast-1.amazonaws.com/private-square/{}'.format(line)
            content = Content(title=title, filepath=url)
            content.save()
            content.tags.add(*tags)
            contents.append(content)
            title = ''
        else:
            title = line
    context['contents'] = contents
    return context

@login_required
def tagging_form(request):
    if not request.user.is_staff:
        messages.add_message(request, messages.INFO, '権限がありません。')
        return redirect('/')
    tags = Tag.objects.all().order_by('name')
    return render(request, 'cms/tagging_form.html', {'tags': tags})

@login_required
def tagging_search(request):
    selected_tags = request.GET.getlist('selected_tags', False)
    tags = Tag.objects.all().order_by('name')
    if not selected_tags:
        selected_tags = []
    else:
        selected_tags = Tag.objects.filter(id__in=selected_tags)
    contents = Content.objects.filter(tags__id__in=selected_tags).order_by('title').distinct()
    context = {
        'tags': tags,
        'selected_tags': selected_tags,
        'contents': contents
    }
    return render(request, 'cms/tagging_search.html', context)

@login_required
def tagging_set(request):
    selected_tags = request.POST.getlist('selected_tags', False)
    selected_contents = request.POST.getlist('selected_contents', False)
    if not selected_tags or not selected_contents:
        messages.add_message(request, messages.INFO, 'タグ・コンテンツを指定してください。')
        return redirect('cms:tagging')
    contents = Content.objects.filter(id__in=selected_contents)
    context = {'contents': contents}
    for content in contents:
        content.tags = selected_tags
        content.save()
    messages.add_message(request, messages.INFO, '{}個のコンテンツを処理しました。'.format(len(contents)))
    return redirect('/')

@login_required
def check(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    checked = Check(user=request.user, content=content)
    checked.save()
    return redirect_to_next(request, 'cms:watch', content_id)

@login_required
def uncheck(request, content_id):
    checked = get_object_or_404(Check, user=request.user, content=content_id)
    checked.delete()
    return redirect_to_next(request, 'cms:watch', content_id)

def redirect_to_next(request, default, *args):
    if 'next' in request.GET:
        return redirect(request.GET['next'], *args)
    else:
        return redirect(default, *args)
