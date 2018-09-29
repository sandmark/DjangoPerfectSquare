from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..models import Content

class IndexViewTests(TestCase):
    def setUp(self):
        """
        ログインする。
        """
        username = 'test@example.com'
        password = 'test'
        u = User(username=username)
        u.set_password(password)
        u.save()
        self.client.login(username=username, password=password)

    def test_no_contents(self):
        """
        Contentが一つもない場合、アラートが表示される。
        """
        count = Content.objects.count()
        r = self.client.get(reverse('cms:index'))
        self.assertEqual(count, 0)
        self.assertContains(r, 'アップロードされたものがありません')
