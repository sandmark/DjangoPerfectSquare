from django.conf.urls import url
from cms import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^watch/(?P<content_id>\d+)/$', views.watch, name='watch'),
    url(r'^watch/(?P<content_id>\d+)/flash/$', views.watch_flash, name='watch_flash'),
    url(r'^watch/(?P<content_id>\d+)/jw/$', views.watch_jw, name='watch_jw'),
    url(r'^tags/(?P<tag_id>\d+)/contents/$', views.tagged_contents, name='tagged_contents'),
    url(r'^contents/(?P<content_id>\d+)/check/$', views.check, name='check'),
    url(r'^contents/(?P<content_id>\d+)/uncheck/$', views.uncheck, name='uncheck'),
]
