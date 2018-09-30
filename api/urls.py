"""
api/urls.py
"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^contents/$', views.ContentList.as_view()),
    url(r'^contents/(?P<pk>\d+)/$', views.ContentDetail.as_view()),
    url(r'tags/$', views.TagList.as_view()),
    url(r'tags/(?P<pk>\d+)/$', views.TagDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
