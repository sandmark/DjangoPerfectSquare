"""
cms/view.py
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import RedirectView

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

class CheckBaseView(View):
    def redirect_to_next(self, request, default, *args, **kwargs):
        dest = request.GET['next'] if 'next' in request.GET else default
        return redirect(dest, *args)

    def get(self, request, *args, **kwargs):
        content = get_object_or_404(Content, pk=kwargs['pk'])
        check = Check.objects.filter(user=request.user, content=content)
        check.delete() if check else Check(user=request.user, content=content).save()
        return self.redirect_to_next(request, 'cms:watch', content.id)
