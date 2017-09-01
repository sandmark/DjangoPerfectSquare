from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404

from .models import Content, Tag

# Create your views here.
@login_required
def index(request):
    recent_contents = Content.objects.all()[:9]
    context = {
        'recent_contents': recent_contents,
        'no_contents': not bool(recent_contents)
    }
    return render(request, 'cms/index.html', context)

@login_required
def watch(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    context = {'content': content}
    return render(request, 'cms/watch.html', context)

@login_required
def tagged_contents(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    contents = Content.objects.filter(tags__id__exact=tag.id)
    context = {'contents': contents, 'tag': tag}
    return render(request, 'cms/tagged_contents.html', context)
