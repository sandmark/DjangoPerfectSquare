from django.test import TestCase
from django.urls import reverse

from ..models import Content
from .helpers import login, create_content

class ThumbnailTest(TestCase):
    def setUp(self):
        login(self.client)

    def test_show_noimage_if_empty(self):
        """
        Content.thumbに値がない（default: 0）場合、
        no_image.pngを表示する。
        """
        c = create_content(title='test', filepath='test.mp4')
        self.assertEqual(Content.objects.count(), 1)
        self.assertFalse(c.thumb)

        r = self.client.get('/')
        self.assertContains(r, 'no_image.png')

    def test_show_thumb_if_not_empty(self):
        """
        Content.thumbに値がある場合、その画像を表示する。
        """
        create_content(title='test', filepath='test.mp4', thumb='test.jpg')

        r = self.client.get('/')
        self.assertContains(r, 'test.jpg')
