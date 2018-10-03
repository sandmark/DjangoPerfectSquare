from django.urls import path
from django.contrib.auth.decorators import login_required
from cms import views

app_name = 'cms'

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('tags/<int:tag_id>/contents/', login_required(views.TagIndexView.as_view()), name='tag_index'),
    path('watch/<int:pk>/',
         login_required(views.WatchView.as_view(template_name='cms/watch_html5.html')),
         name='watch'),
    path('watch/<int:pk>/flash/',
         login_required(views.WatchView.as_view(template_name='cms/watch_flash.html')),
         name='watch_flash'),
    path('watch/<int:pk>/jw/',
         login_required(views.WatchView.as_view(template_name='cms/watch_jw.html')),
         name='watch_jw'),
    path('contents/<int:pk>/check/', login_required(views.CheckBaseView.as_view()), name='check'),
    path('contents/<int:pk>/uncheck/', login_required(views.CheckBaseView.as_view()), name='uncheck'),
]
