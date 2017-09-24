"""
api/urls.py
"""
from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^contents/$', views.content_list),
    url(r'^contents/(?P<pk>\d+)/$', views.content_detail),
]
