import urllib
from django.test import TestCase

from ..models import Content, Check
from .helpers import create_content, create_user, is_s3_exists, s3_delete, s3_upload

test_file = 'cms/tests/test.mp4'

class ContentTest(TestCase):
    def test_if_content_check_deletion(self):
        """
        Contentが削除されたタイミングで
        関連付けられたCheckも同様に削除される。
        """
        c = create_content()
        u = create_user()
        ch = Check(user=u, content=c)
        ch.save()
        self.assertEqual(Check.objects.count(), 1)
        c.delete()
        self.assertEqual(Check.objects.count(), 0)

    def test_file_delete_when_content_deleted(self):
        """
        Contentレコードが削除されると同時にS3上にあるファイルも削除される。
        """
        dest = s3_upload(test_file)

        url = urllib.parse.urlparse(dest)[2].split('/')[2:]
        url = '/'.join(url)

        content = Content(title='delete_test', filepath=dest)
        content.save()
        content.delete()
        existance = is_s3_exists(test_file)
        self.assertFalse(existance)

        s3_delete(test_file)
