from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect

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
    contents = Content.objects.filter(tags__id__exact=tag.id).order_by('title')
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
    for line in context['text_contents'].split('\n'):
        if title:
            url = 'https://s3-ap-northeast-1.amazonaws.com/private-square/{}'.format(line)
            content = Content(title=title, filepath=url)
            content.save()
            content.tags = context['tags']
            contents.append(content)
            title = ''
        else:
            title = line
    context['contents'] = contents
    return context
