"""
Data serializer classes of Django Rest Framework.
"""
from rest_framework import serializers
from cms.models import Content
from cms.models import Tag


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ('id', 'title', 'filepath')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')
