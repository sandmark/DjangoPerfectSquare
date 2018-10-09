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
    paginate_by = 9
    ordering = ['-created']
    context_object_name = 'contents'
    template_name = 'cms/index.haml'

class TagIndexView(ListView):
    model = Content
    paginate_by = 9
    context_object_name = 'contents'
    template_name = 'cms/tag_index.haml'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs['tag_id'])
        return Content.objects.filter(tags__id__exact=tag.id).order_by('title')

    def get_context_data(self, **kwargs):
        tag = get_object_or_404(Tag, pk=self.kwargs['tag_id'])
        context = super().get_context_data(**kwargs)
        context['tag'] = tag
        return context

class WatchView(DetailView):
    model = Content
    context_object_name = 'content'

    def get_object(self, queryset=None):
        content = super(WatchView, self).get_object(queryset=queryset)
        content.update_thumbnail()
        content.save()
        return content
    

class CheckBaseView(View):
    def redirect_to_next(self, request, default, *args, **kwargs):
        dest = request.POST['next'] if 'next' in request.POST else default
        return redirect(dest, *args)

    def post(self, request, *args, **kwargs):
        content = get_object_or_404(Content, pk=kwargs['pk'])
        check = Check.objects.filter(user=request.user, content=content)
        check.delete() if check else Check(user=request.user, content=content).save()
        return self.redirect_to_next(request, 'cms:watch', content.id)
