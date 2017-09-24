"""
api/urls.py
"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^contents/$', views.content_list),
    url(r'^contents/(?P<pk>\d+)/$', views.content_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)
