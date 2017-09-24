"""
api/views.py
"""
from cms.models import Content
from api.serializers import ContentSerializer
from rest_framework import generics


class ContentList(generics.ListCreateAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer


class ContentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
