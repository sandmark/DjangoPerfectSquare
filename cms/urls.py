from django.urls import path
from django.contrib.auth.decorators import login_required
from cms import views

app_name = 'cms'

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('tags/<int:tag_id>/contents/', login_required(views.TagIndexView.as_view()), name='tag_index'),
    path('watch/<int:content_id>/', views.watch, name='watch'),
    path('watch/<int:content_id>/flash/', views.watch_flash, name='watch_flash'),
    path('watch/<int:content_id>/jw/', views.watch_jw, name='watch_jw'),
    path('contents/<int:content_id>/check/', views.check, name='check'),
    path('contents/<int:content_id>/uncheck/', views.uncheck, name='uncheck'),
]
