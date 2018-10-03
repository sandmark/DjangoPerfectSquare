from django.db import models
from s3direct.fields import S3DirectField
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

# Create your models here.


class Tag(models.Model):
    """タグ"""
    name = models.CharField('名前', max_length=255, unique=True, blank=False)
    sites = models.ManyToManyField(Site)

    def __str__(self):
        return self.name


class Content(models.Model):
    """コンテンツ"""
    title = models.CharField('タイトル', max_length=255, blank=False)
    filepath = S3DirectField(dest='square', unique=True)
    created = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    sites = models.ManyToManyField(Site)

    def __str__(self):
        return self.title


class Check(models.Model):
    """視聴済みマーク"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

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

# So these code below delete S3 file intended by Content.filepath
# when Content was deleted, however,
# I still want to solve this problem smarter than this.

from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
import urllib
from boto3.session import Session
from botocore.exceptions import ClientError
from django.conf import settings

def is_s3_exists(s3, bucket_name, key):
    try:
        s3.Object(bucket_name, key).load()
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e
    else:
        return True

@receiver(post_delete, sender=Content)
def content_delete_file_from_s3(sender, instance, **kwargs):
    # Parse URI to S3Key
    parts = urllib.parse.urlparse(instance.filepath)[2].split('/')[2:]
    key = '/'.join(parts)
    if key:
        session = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.S3DIRECT_REGION)
        s3 = session.resource('s3')
        if is_s3_exists(s3, settings.AWS_STORAGE_BUCKET_NAME, key):
            s3.Object(settings.AWS_STORAGE_BUCKET_NAME, key).delete()
