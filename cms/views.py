"""
cms/view.py
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from pure_pagination import Paginator, PageNotAnInteger
from .models import Content, Tag, Check

@login_required
def index(request):
    """
    Contentをすべて取得し、ページネーションして描画する。
    """
    all_contents = Content.objects.all().order_by('-created')
    page = request.GET.get('page', 1)
    p = Paginator(all_contents, 10, request=request)

    try:
        contents = p.page(page)
    except PageNotAnInteger:
        contents = p.page(1)

    context = {'contents': contents}
    return render(request, 'cms/index.html', context)


@login_required
def watch(request, content_id):
    """
    HTML5プレイヤーを表示する
    """
    return render_content(content_id, 'cms/watch_html5.html', request)


@login_required
def watch_flash(request, content_id):
    """
    Flashプレイヤーを表示する
    """
    return render_content(content_id, 'cms/watch_flash.html', request)


@login_required
def watch_jw(request, content_id):
    """
    JW Playerを表示する
    """
    return render_content(content_id, 'cms/watch_jw.html', request)


def render_content(content_id, template, request):
    """
    Helper function.
    指定されたContent#idで検索し、指定されたテンプレートを描画する
    """
    content = get_object_or_404(Content, pk=content_id)
    return render(request, template, {'content': content})


@login_required
def tagged_contents(request, tag_id):
    """
    指定されたタグを含むContentを描画する
    """
    tag = get_object_or_404(Tag, pk=tag_id)
    all_contents = Content.objects.filter(tags__id__exact=tag.id).order_by('title')

    page = request.GET.get('page', 1)

    p = Paginator(all_contents, 10, request=request)

    try:
        contents = p.page(page)
    except PageNotAnInteger:
        contents = p.page(1)

    context = {'contents': contents, 'tag': tag}
    return render(request, 'cms/tagged_contents.html', context)


@login_required
def tagging_form(request):
    """
    Contentにタグ付けするフォームを表示する
    """
    if not request.user.is_staff:
        messages.add_message(request, messages.INFO, '権限がありません。')
        return redirect('/')
    tags = Tag.objects.all().order_by('name')
    return render(request, 'cms/tagging_form.html', {'tags': tags})


@login_required
def tagging_search(request):
    """
    選択されたタグを付けられたContentを検索し、フォームを表示する
    """
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
    """
    選択されたタグをコンテントに関連付ける
    """
    selected_tags = request.POST.getlist('selected_tags', False)
    selected_contents = request.POST.getlist('selected_contents', False)
    if not selected_tags or not selected_contents:
        messages.add_message(request, messages.INFO, 'タグ・コンテンツを指定してください。')
        return redirect('cms:tagging')
    contents = Content.objects.filter(id__in=selected_contents)
    for content in contents:
        content.tags = selected_tags
        content.save()
    messages.add_message(request, messages.INFO, '{}個のコンテンツを処理しました。'.format(len(contents)))
    return redirect('/')


@login_required
def check(request, content_id):
    """
    指定されたコンテントにチェックを付ける
    """
    content = get_object_or_404(Content, pk=content_id)
    checked = Check(user=request.user, content=content)
    checked.save()
    return redirect_to_next(request, 'cms:watch', content_id)


@login_required
def uncheck(request, content_id):
    """
    指定されたコンテントからチェックを外す
    """
    checked = get_object_or_404(Check, user=request.user, content=content_id)
    checked.delete()
    return redirect_to_next(request, 'cms:watch', content_id)


def redirect_to_next(request, default, *args):
    """
    Helper.
    nextパラメータが指定されている場合、そちらにリダイレクトする。
    そうでなければ指定されたページへリダイレクトする。
    """
    if 'next' in request.GET:
        return redirect(request.GET['next'], *args)
    else:
        return redirect(default, *args)
