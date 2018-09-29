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

    def test_page_not_an_integer(self):
        """
        ?page=a などでアクセスされてもエラーを吐かない。
        """
        url = reverse('cms:index')
        location = '{}?page=something'.format(url)
        r = self.client.get(location)
        self.assertEqual(r.status_code, 200)

    def test_contents_sorted_by_created(self):
        """
        Contentは最近作られたものから表示される。
        """
        url = reverse('cms:index')
        for i in range(10):
            c = Content(title=str(i), filepath=i)
            c.save()
        r = self.client.get(url)
        contents = r.context['contents'].object_list
        for i, content in enumerate(reversed(contents)):
            self.assertEquals(content.title, str(i))

    def test_contents_paginated_by_ten(self):
        """
        Contentは10個ずつページネーションされる。
        """
        url = reverse('cms:index')
        for i in range(20):
            name = str(i)
            Content(title=name, filepath=name).save()
        r = self.client.get(url)
        contents = r.context['contents'].object_list
        self.assertEquals(len(contents), 10)

    def test_pagination_shows_at_most_five_pages(self):
        """
        ページが6以上ある場合でも5つまでしか表示しない。
        """
        url = reverse('cms:index')
        for i in range(100):
            name = str(i)
            Content(title=name, filepath=name).save()
        r = self.client.get(url)
        self.assertContains(r, 'page-item', 5+2) # last 2 means `prev` and `next` link
