from django.urls import path
from cms import views

app_name = 'cms'

urlpatterns = [
    path('', views.index, name='index'),
    path('watch/<int:content_id>/', views.watch, name='watch'),
    path('watch/<int:content_id>/flash/', views.watch_flash, name='watch_flash'),
    path('watch/<int:content_id>/jw/', views.watch_jw, name='watch_jw'),
    path('tags/<int:tag_id>/contents/', views.tagged_contents, name='tagged_contents'),
    path('contents/<int:content_id>/check/', views.check, name='check'),
    path('contents/<int:content_id>/uncheck/', views.uncheck, name='uncheck'),
]
