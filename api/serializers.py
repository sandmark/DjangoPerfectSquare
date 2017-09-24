"""
Data serializer classes of Django Rest Framework.
"""
from rest_framework import serializers
from cms.models import Content
from cms.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class ContentSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Content
        fields = ('id', 'title', 'filepath', 'tags')
