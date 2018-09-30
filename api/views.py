"""
api/views.py
"""
from cms.models import Content, Tag
from api.serializers import ContentSerializer, TagSerializer
from rest_framework import generics, permissions


class ContentList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Content.objects.all()
    serializer_class = ContentSerializer


class ContentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Content.objects.all()
    serializer_class = ContentSerializer


class TagList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """
        `tagname`クエリパラメータがURLに含まれている場合
        クエリ結果をフィルタリングして返す
        """
        queryset = Tag.objects.all()
        tagname = self.request.query_params.get('tagname', None)
        if tagname is not None:
            queryset = queryset.filter(name=tagname)
        return queryset


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
