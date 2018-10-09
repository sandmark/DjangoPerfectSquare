import os

from django.db import models
from s3direct.fields import S3DirectField
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from .utils import uri2key, is_key_exists, s3_delete_key, s3_upload_thumbnail, generate_thumbnail


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

    def update_thumbnail(self):
        """
        filepathの拡張子が.mp4であり、かつthumbが空である場合にサムネイルを自動生成する。
        """
        if self.filepath and self.filepath.endswith('mp4'):
            if self.thumb == 'false' or not self.thumb:
                thumb = generate_thumbnail(self.title, self.filepath)
                if os.path.exists(thumb):
                    url = s3_upload_thumbnail(thumb)
                    self.thumb = url

    def __str__(self):
        return self.title


class Check(models.Model):
    """視聴済みマーク"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Content)
def content_generate_thumbnail(sender, instance, **kwargs):
    """
    Contentが保存されるときにupdate_thumbnail()を呼び出す。
    """
    instance.update_thumbnail()

@receiver(post_delete, sender=Content)
def content_delete_file_from_s3(sender, instance, **kwargs):
    """
    filepathとthumbがS3上に存在する場合、Contentレコードが削除されたあと同様に削除する。
    """
    for uri in [instance.filepath, instance.thumb]:
        key = uri2key(uri)
        if key and is_key_exists(key):
            s3_delete_key(key)
