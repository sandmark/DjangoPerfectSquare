"""
Data serializer classes of Django Rest Framework.
"""
from rest_framework import serializers
from cms.models import Content


class ContentSerializer(serializers.ModelSerializer):
    """Contentのシリアライズを行う"""
    class Meta:
        model = Content
        fields = ('id', 'title', 'filepath')
