"""
api/views.py
"""
from cms.models import Content, Tag
from api.serializers import ContentSerializer, TagSerializer
from rest_framework import generics, permissions


class ContentList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Content.objects.all()
    serializer_class = ContentSerializer


class ContentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Content.objects.all()
    serializer_class = ContentSerializer


class TagList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
