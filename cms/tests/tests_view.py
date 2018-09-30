from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..models import Content, Tag

def login(client):
    """
    Login as normal user (not admin or staff)
    """
    username = 'test@example.com'
    password = 'test'
    u = User(username=username)
    u.set_password(password)
    u.save()
    return client.login(username=username, password=password)

def create_content(title='test', filepath='http://example.com/something.mp4'):
    c = Content(title=title, filepath=filepath)
    c.save()
    return c

class WatchViewTests(TestCase):
    def setUp(self):
        login(self.client)

    def test_watch_views_404_if_id_not_found(self):
        """
        cms:watch, cms:watch_flash, cms:watch_jwに存在しないContentが
        指定された場合、404エラーを返す。
        """
        count = Content.objects.count()
        self.assertEqual(count, 0)

        for url in ['cms:watch', 'cms:watch_flash', 'cms:watch_jw']:
            url = reverse(url, kwargs={'content_id': 1})
            r = self.client.get(url)
            self.assertEqual(r.status_code, 404)

    def test_watch_views_404_if_invalid_id(self):
        """
        cms:watch, cms:watch_flash, cms:watch_jwに
        無効なcontent_idが指定された場合、404エラーを返す。
        """
        for url in ['/watch/{}', '/watch/{}/flash', '/watch/{}/jw']:
            r = self.client.get(url.format('string'))
            self.assertEqual(r.status_code, 404)

    def test_watch_renders_html5_if_mp4(self):
        """
        cms:watchはhtml5プレイヤーを表示する。
        """
        c = create_content()
        url = reverse('cms:watch', kwargs={'content_id': c.id})
        r = self.client.get(url)
        self.assertContains(r, '<video')

    def test_watch_jw_renders_jwplayer_if_mp4(self):
        """
        cms:jwはjwplayerを表示する。
        """
        c = create_content()
        url = reverse('cms:watch_jw', kwargs={'content_id': c.id})
        r = self.client.get(url)
        self.assertContains(r, 'jwplayer')

    def test_watch_flash_renders_flash_if_mp4(self):
        """
        cms:flashはFlashプレイヤーを表示する。
        """
        c = create_content()
        url = reverse('cms:watch_flash', kwargs={'content_id': c.id})
        r = self.client.get(url)
        self.assertContains(r, 'shockwave-flash')

class MixinIndexTag():
    """
    MixIn class to test `index` and `tagged_contents` views.
    """
    @property
    def url(self):
        raise NotImplementedError

    @property
    def params(self):
        raise NotImplementedError

    @property
    def make_contents(self, count):
        raise NotImplementedError

    def test_page_not_an_integer(self):
        """
        ?page=a などでアクセスされてもエラーを吐かない。
        """
        url = reverse(self.url, kwargs=self.params)
        r = self.client.get(url, {'page': 'something'})
        self.assertEqual(r.status_code, 200)

    def test_contents_paginated_by_ten(self):
        """
        Contentは10個ずつページネーションされる。
        """
        url = reverse(self.url, kwargs=self.params)
        self.make_contents(20)
        r = self.client.get(url)
        contents = r.context['contents'].object_list
        self.assertEquals(len(contents), 10)

    def test_pagination_shows_at_most_five_pages(self):
        """
        ページが6以上ある場合でも5つまでしか表示しない。
        """
        url = reverse(self.url, kwargs=self.params)
        self.make_contents(100)
        r = self.client.get(url)
        self.assertContains(r, 'page-item', 5+2) # last 2 means `prev` and `next` link

class IndexViewTest(MixinIndexTag, TestCase):
    def setUp(self):
        login(self.client)

    def make_contents(self, count):
        for i in range(count):
            name = str(i)
            Content(title=name, filepath=name).save()

    url = 'cms:index'
    params = {}
    make_contents = make_contents

    def test_no_contents(self):
        """
        Contentが一つもない場合、アラートが表示される。
        """
        count = Content.objects.count()
        r = self.client.get(reverse(self.url, kwargs=self.params))
        self.assertEqual(count, 0)
        self.assertContains(r, 'アップロードされたものがありません')

    def test_contents_sorted_by_created(self):
        """
        Contentは最近作られたものから表示される。
        """
        url = reverse(self.url, kwargs=self.params)
        for i in range(10):
            Content(title=str(i), filepath=i).save()
        r = self.client.get(url)
        contents = r.context['contents'].object_list
        for i, content in enumerate(reversed(contents)):
            self.assertEquals(content.title, str(i))

class TaggedViewTest(MixinIndexTag, TestCase):
    def make_contents(self, count):
        t = Tag.objects.get(pk=1)
        for i in range(count):
            name = str(i)
            c = Content(title=name, filepath=name)
            c.save()
            c.tags.add(t)

    url = 'cms:tagged_contents'
    params = {'tag_id': 1}
    make_contents = make_contents

    def setUp(self):
        login(self.client)
        t = Tag(name='testTag')
        t.save()

    def test_404_for_tag_dont_exists(self):
        """
        存在しないTagを指定された場合404となる。
        """
        url = reverse(self.url, kwargs={'tag_id': 404})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)
