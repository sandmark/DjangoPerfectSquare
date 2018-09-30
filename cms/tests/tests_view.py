from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..models import Content, Tag, Check
from .helpers import login, create_content

class MixinCheck():
    @property
    def urlname(self):
        raise NotImplementedError

    @property
    def create_content(self):
        raise NotImplementedError

    def test_check_404_content_not_found(self):
        """
        指定されたContentが存在しない場合404エラーを返す。
        """
        url = reverse(self.urlname, kwargs={'content_id': 404})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)

    def test_check_redirect_to_next(self):
        """
        ?nextパラメータが指定されている場合、そちらにリダイレクトする。
        """
        c = self.create_content()
        url = reverse(self.urlname, kwargs={'content_id': c.id})
        r = self.client.get(url, {'next': '/'})
        self.assertRedirects(r, '/')

    def test_check_redirect_to_default(self):
        """
        ?nextパラメータが指定されなかった場合、
        デフォルトで cms:watch へリダイレクトする。
        """
        c = self.create_content()
        url = reverse(self.urlname, kwargs={'content_id': c.id})
        redirected = reverse('cms:watch', kwargs={'content_id': c.id})
        r = self.client.get(url)
        self.assertRedirects(r, redirected)

class CheckTest(MixinCheck, TestCase):
    def setUp(self):
        login(self.client)

    def create_content(self):
        return create_content()

    urlname = 'cms:check'
    create_content = create_content

    def test_check_creation(self):
        """
        対象ContentとUserの間にCheckオブジェクトが生成される。
        """
        c = self.create_content()
        url = reverse(self.urlname, kwargs={'content_id': c.id})
        self.client.get(url)
        count = Check.objects.count()
        self.assertEqual(count, 1)

class UncheckTest(MixinCheck, TestCase):
    def setUp(self):
        login(self.client)

    def create_content(self):
        """
        Checkオブジェクトを保存しておかないと
        get_object_or_404のタイミングで404となってしまうため、
        テスト用Contentを作るときに関連付けておく。
        """
        c = create_content()
        u = User.objects.first()
        ch = Check(user=u, content=c)
        ch.save()
        return c

    urlname = 'cms:uncheck'
    create_content = create_content

    def test_check_deletion(self):
        """
        対象ContentとUserの間からCheckオブジェクトが削除される。
        """
        c = create_content()
        url = reverse(self.urlname, kwargs={'content_id': c.id})
        user = User.objects.first()
        Check(user=user, content=c).save()
        self.client.get(url)
        self.assertEqual(Check.objects.count(), 0)

class MixinWatch():
    @property
    def url_name(self):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError

    @property
    def contains(self):
        raise NotImplementedError

    def test_watch_views_404_if_id_not_found(self):
        """
        存在しないContentが指定された場合、404エラーを返す。
        """
        count = Content.objects.count()
        self.assertEqual(count, 0)
        url = reverse(self.url_name, kwargs={'content_id': 1})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)

    def test_watch_views_404_if_invalid_id(self):
        """
        無効なcontent_idが指定された場合、404エラーを返す。
        """
        r = self.client.get(self.url.format('something'))
        self.assertEqual(r.status_code, 404)

    def test_watch_renders_player_if_mp4(self):
        """
        cms:watchはhtml5プレイヤーを表示する。
        """
        c = create_content()
        url = reverse(self.url_name, kwargs={'content_id': c.id})
        r = self.client.get(url)
        self.assertContains(r, self.contains)

class WatchViewTest(MixinWatch, TestCase):
    def setUp(self):
        login(self.client)

    url_name = 'cms:watch'
    url = 'cms/watch/{}'
    contains = '<video'

class WatchJwViewTest(MixinWatch, TestCase):
    def setUp(self):
        login(self.client)

    url_name = 'cms:watch_jw'
    url = 'cms/watch/{}/jw'
    contains = 'jwplayer'

class WatchFlashViewTest(MixinWatch, TestCase):
    def setUp(self):
        login(self.client)

    url_name = 'cms:watch_flash'
    url = 'cms/watch/{}/flash'
    contains = 'shockwave-flash'


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

    def test_with_contents(self):
        """
        Contentが一つ以上ある場合、アラートは表示されない。
        """
        create_content()
        self.assertEqual(Content.objects.count(), 1)
        r = self.client.get(reverse(self.url, kwargs=self.params))
        self.assertNotContains(r, 'アップロードされたものがありません')

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

    def test_contents_sorted_by_title(self):
        """
        ContentはTitleでソートされて表示される。
        """
        self.make_contents(10)
        url = reverse(self.url, kwargs=self.params)
        r = self.client.get(url)
        contents = r.context['contents'].object_list
        for i, content in enumerate(contents):
            self.assertEqual(str(i), content.title)
