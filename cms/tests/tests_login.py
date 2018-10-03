from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User

username = 'test@exanmple.com'
password = 'test'

def login(client):
    return client.login(username=username, password=password)

class LoginTests(TestCase):
    def test_login_page(self):
        """
        ログインフォームが表示される。
        """
        r = self.client.get('/accounts/login/')
        self.assertContains(r, 'ログイン')

class IndexViewTests(TestCase):
    def setUp(self):
        """
        ログイン可能なユーザを一名追加しておく。
        """
        u = User(username=username)
        u.set_password(password)
        u.save()

    def test_index_without_logged_in(self):
        """
        ログインしていない状態で訪れると、ログインページにリダイレクトされる。
        """
        url = reverse('cms:index')
        r = self.client.get(url)
        self.assertRedirects(r, '/accounts/login/?next={}'.format(url))

    def test_index_with_logged_in(self):
        """
        ログインできた場合 index が表示される。
        """
        url = reverse('cms:index')
        login(self.client)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
