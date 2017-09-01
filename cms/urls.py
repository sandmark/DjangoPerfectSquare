from django.conf.urls import url
from cms import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
