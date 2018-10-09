from django.test import TestCase
from django.urls import reverse

from ..models import Content
from .helpers import login, create_content, s3_upload, s3_delete, is_s3_exists

test_file = 'cms/tests/test.mp4'
test_thumbnail = 'cms/tests/test.jpg'

class ThumbnailTest(TestCase):
    def setUp(self):
        login(self.client)

    def tearDown(self):
        s3_delete(test_file)
        s3_delete(test_thumbnail)

    def test_show_noimage_if_empty(self):
        """
        Content.thumbに値がない（default: 0）場合、
        no_image.pngを表示する。
        """
        c = create_content(title='test', filepath='test.rar')
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

    def test_thumbnail_generate_not_mp4(self):
        """
        mp4ファイルでない場合はサムネイルを自動生成しない。
        """
        c = create_content(title='test', filepath='test.rar')
        self.assertFalse(c.thumb)

    def test_thumbnail_generate_mp4(self):
        """
        mp4ファイルである場合、サムネイルを自動生成する。
        """
        url = s3_upload(test_file)
        c = create_content(title='test', filepath=url)
        self.assertEqual(Content.objects.count(), 1)
        self.assertIn('.jpg', c.thumb)

    def test_thumbnail_delete(self):
        """
        Contentが削除されたとき、サムネイルも削除される。
        """
        thumbnail_url = s3_upload(test_thumbnail)
        c = create_content(title='test', thumb=thumbnail_url)
        c.delete()
        self.assertFalse(is_s3_exists(test_thumbnail))

    def test_generated_thumbnail_delete(self):
        """
        Contentが削除されたとき、自動生成されたサムネイルも削除される。
        """
        url = s3_upload(test_file)
        c = create_content(title='thumb_generate', filepath=url)
        self.assertEqual(Content.objects.count(), 1)
        self.assertTrue(is_s3_exists(filename='thumb-thumb_generate.jpg', key='thumbnails'))
        c.delete()
        self.assertEqual(Content.objects.count(), 0)
        self.assertFalse(is_s3_exists(filename='thumb-thumb_generate.jpg', key='thumbnails'))
