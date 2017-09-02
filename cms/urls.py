from django.conf.urls import url
from cms import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^watch/(?P<content_id>\d+)/$', views.watch, name='watch'),
    url(r'^tags/(?P<tag_id>\d+)/contents/$', views.tagged_contents, name='tagged_contents'),
]
