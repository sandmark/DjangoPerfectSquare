from django.test import TestCase

from ..models import Content, Check
from .helpers import create_content, create_user

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
