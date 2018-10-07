from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..models import Content, Tag, Check
from .helpers import login, create_content

class LayoutViewTest(TestCase):
    def test_show_admin_menu_only_admin_user(self):
        """
        AdminメニューはAdminにのみ表示される。
        """
        login(self.client)
        r = self.client.get('/')
        self.assertNotContains(r, "Admin")

        u = User(username='admin', is_staff=True)
        u.set_password('admin')
        u.save()
        self.client.login(username=u.username, password='admin')
        r = self.client.get('/')
        self.assertContains(r, 'Admin')

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
        url = reverse(self.urlname, kwargs={'pk': 404})
        r = self.client.post(url)
        self.assertEqual(r.status_code, 404)

    def test_check_redirect_to_next(self):
        """
        ?nextパラメータが指定されている場合、そちらにリダイレクトする。
        """
        c = self.create_content()
        url = reverse(self.urlname, kwargs={'pk': c.id})
        r = self.client.post(url, {'next': '/'})
        self.assertRedirects(r, '/')

    def test_check_redirect_to_default(self):
        """
        ?nextパラメータが指定されなかった場合、
        デフォルトで cms:watch へリダイレクトする。
        """
        c = self.create_content()
        url = reverse(self.urlname, kwargs={'pk': c.id})
        redirected = reverse('cms:watch', kwargs={'pk': c.id})
        r = self.client.post(url)
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
        url = reverse(self.urlname, kwargs={'pk': c.id})
        self.client.post(url)
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
        url = reverse(self.urlname, kwargs={'pk': c.id})
        user = User.objects.first()
        Check(user=user, content=c).save()
        self.client.post(url)
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
        url = reverse(self.url_name, kwargs={'pk': 1})
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
        url = reverse(self.url_name, kwargs={'pk': c.id})
        r = self.client.get(url)
        self.assertContains(r, self.contains)

class WatchViewTest(MixinWatch, TestCase):
    def setUp(self):
        login(self.client)

    url_name = 'cms:watch'
    url = 'cms/watch/{}'
    contains = '<video'

# class WatchJwViewTest(MixinWatch, TestCase):
#     def setUp(self):
#         login(self.client)

#     url_name = 'cms:watch_jw'
#     url = 'cms/watch/{}/jw'
#     contains = 'jwplayer'

# class WatchFlashViewTest(MixinWatch, TestCase):
#     def setUp(self):
#         login(self.client)

#     url_name = 'cms:watch_flash'
#     url = 'cms/watch/{}/flash'
#     contains = 'shockwave-flash'


class MixinIndexTag():
    """
    MixIn class to test `index` and `tag_index` views.
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

    @property
    def create_content(title, filepath):
        raise NotImplementedError

    def test_show_contents(self):
        """
        Content.titleが表示される。
        """
        self.create_content(title='TestContent', filepath='nil')
        url = reverse(self.url, kwargs=self.params)
        r = self.client.get(url)
        self.assertContains(r, 'TestContent')

    def test_page_not_an_integer(self):
        """
        ?page=a など無効なページが指定された場合404エラーを返す。
        """
        url = reverse(self.url, kwargs=self.params)
        r = self.client.get(url, {'page': 'something'})
        self.assertEqual(r.status_code, 404)

    def test_first_page_when_contents_empty(self):
        """
        Contentがない場合に page=2 などへアクセスされた場合
        404エラーを返す。
        """
        self.assertEqual(Content.objects.count(), 0)
        url = reverse(self.url, kwargs=self.params)
        r = self.client.get(url, {'page': '2'})
        self.assertEqual(r.status_code, 404)

    def test_contents_paginated_by_ten(self):
        """
        Contentは10個ずつページネーションされる。
        """
        url = reverse(self.url, kwargs=self.params)
        self.make_contents(20)
        r = self.client.get(url)
        contents = r.context['contents']
        self.assertEqual(len(contents), 10)

    def test_pagination_shows_at_most_three_pages(self):
        """
        ページリンクは最大5つまでしか表示しない。
        上下のページネーションを合わせて10のリンクが生成される。
        """
        url = reverse(self.url, kwargs=self.params)
        self.make_contents(100)
        r = self.client.get(url, {'page': 2})
        self.assertContains(r, 'page-item', 5*2)

class IndexViewTest(MixinIndexTag, TestCase):
    def setUp(self):
        login(self.client)

    def make_contents(self, count):
        for i in range(count):
            name = str(i)
            Content(title=name, filepath=name).save()

    def create_content(self, title, filepath):
        return create_content(title, filepath)

    url = 'cms:index'
    params = {}
    make_contents = make_contents
    create_content = create_content

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
        contents = r.context['contents']
        for i, content in enumerate(reversed(contents)):
            self.assertEqual(content.title, str(i))

class TagIndexViewTest(MixinIndexTag, TestCase):
    def create_content(self, title, filepath):
        tag = Tag.objects.get(pk=1)
        c = create_content(title, filepath)
        c.save()
        c.tags.add(tag)
        return c

    def make_contents(self, count):
        t = Tag.objects.get(pk=1)
        for i in range(count):
            name = str(i)
            c = Content(title=name, filepath=name)
            c.save()
            c.tags.add(t)

    url = 'cms:tag_index'
    params = {'tag_id': 1}
    make_contents = make_contents
    create_content = create_content

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
        contents = r.context['contents']
        for i, content in enumerate(contents):
            self.assertEqual(str(i), content.title)
