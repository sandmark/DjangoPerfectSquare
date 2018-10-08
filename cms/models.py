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
    thumb = S3DirectField(dest='thumbnails', blank=True, default=False)
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

import os
import subprocess
import urllib

from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from .utils import uri2key, is_key_exists, s3_delete_key, s3_upload_thumbnail, make_hash

@receiver(post_save, sender=Content)
def content_generate_thumbnail(sender, instance, created, **kwargs):
    """
    Contentが作成されるとき、filepathの拡張子が.mp4であり、
    かつthumbが空である場合にサムネイルを自動生成する。
      10秒の位置で320x240のサムネイルを作成する場合:
        ffmpeg -i #{VIDEO}.mp4 -ss 10 -vframes 1 -f image2 -s 320x240 #{VIDEO}.jpg
    """
    if created and instance.filepath and instance.filepath.endswith('mp4') and not instance.thumb:
        thumb_hash = make_hash(instance.title)
        thumb = '/tmp/thumb-{}.jpg'.format(thumb_hash)
        fileurl = urllib.parse.quote(instance.filepath, safe=':/')
        ffmpeg = 'ffmpeg -y -i "{filepath}" -ss 0 -vframes 1 -f image2 -s 320x240 {thumb}'
        subprocess.call(ffmpeg.format(filepath=fileurl, thumb=thumb), shell=True)

        if os.path.exists(thumb):
            url = s3_upload_thumbnail(thumb)
            instance.thumb = url

@receiver(post_delete, sender=Content)
def content_delete_file_from_s3(sender, instance, **kwargs):
    """
    filepathとthumbがS3上に存在する場合、Contentレコードが削除されたあと同様に削除する。
    """
    for uri in [instance.filepath, instance.thumb]:
        key = uri2key(uri)
        if key and is_key_exists(key):
            s3_delete_key(key)
