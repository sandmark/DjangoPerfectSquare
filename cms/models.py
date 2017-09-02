from django.db import models
from s3direct.fields import S3DirectField
from django.contrib.sites.models import Site

# Create your models here.
class Tag(models.Model):
    """タグ"""
    name  = models.CharField('名前', max_length=255, unique=True)
    sites = models.ManyToManyField(Site)

    def __str__(self):
        return self.name

class Content(models.Model):
    """コンテンツ"""
    title    = models.CharField('タイトル', max_length=255)
    filepath = S3DirectField(dest='square')
    tags     = models.ManyToManyField(Tag)
    sites    = models.ManyToManyField(Site)

    def __str__(self):
        return self.title

# Receive the pre_delete signal and delete the file associated with the model instance.
# !! S3Direct
#      while s3direct is activated, the `filepath` attribute has been changed to
#      `str` object so these code would occur an exception named
#      AttributeError('str' object has no attribute 'delete').
#
# from django.db.models.signals import pre_delete
# from django.dispatch.dispatcher import receiver

# @receiver(pre_delete, sender=Content)
# def content_delete(sender, instance, **kwargs):
#     if instance.filepath:
#         instance.filepath.delete(False)