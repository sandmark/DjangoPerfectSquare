from django.conf.urls import url
from cms import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^watch/(?P<content_id>\d+)/$', views.watch, name='watch'),
    url(r'^tags/(?P<tag_id>\d+)/contents/$', views.tagged_contents, name='tagged_contents'),
    url(r'^private-square/register/$', views.register_from_file, name='register_file'),
    url(r'^tagging/form/$', views.tagging_form, name='tagging'),
    url(r'^tagging/search/$', views.tagging_search, name='tag_search'),
    url(r'^tagging/set/$', views.tagging_set, name='tag_set'),
]
