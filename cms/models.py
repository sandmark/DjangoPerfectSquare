from django.db import models

# Create your models here.
class Tag(models.Model):
    """タグ"""
    name = models.CharField('名前', max_length=255)

    def __str__(self):
        return self.name

class Content(models.Model):
    """コンテンツ"""
    title    = models.CharField('タイトル', max_length=255)
    filepath = models.FileField(upload_to='video/', max_length=255)
    tags     = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title
