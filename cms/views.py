from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Content

# Create your views here.
@login_required
def index(request):
    recent_contents = Content.objects.all()[:9]
    context = {
        'recent_contents': recent_contents,
        'no_contents': not bool(recent_contents)
    }
    return render(request, 'cms/index.html', context)
