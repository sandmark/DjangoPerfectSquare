"""
cms/view.py
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView

from .models import Content, Tag, Check

class IndexView(ListView):
    model = Content
    paginate_by = 10
    ordering = ['-created']
    context_object_name = 'contents'
    template_name = 'cms/index.html'

class TagIndexView(ListView):
    model = Content
    paginate_by = 10
    context_object_name = 'contents'
    template_name = 'cms/tag_index.html'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs['tag_id'])
        return Content.objects.filter(tags__id__exact=tag.id).order_by('title')

class WatchView(DetailView):
    model = Content
    context_object_name = 'content'

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
