from mock import patch
from django.test import TestCase
try:
    from django.urls import reverse_lazy as reverse
except ImportError:
    # Django 1.0
    from django.core.urlresolvers import reverse_lazy as reverse

from . import factories


class TorrentListViewTest(TestCase):
    url = reverse('torrent')

    def setUp(self):
        self.user = factories.UserFactory()
        self.client.login(username=self.user.username,
                          password='foobarham')

    def test_get(self):
        factories.TorrentFactory.build_batch(3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TorrentDetailViewTest(TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.client.login(username=self.user.username,
                          password='foobarham')

    def test_get(self):
        torrent = factories.TorrentFactory()
        url = torrent.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TorrentActionViewTest(TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.client.login(username=self.user.username,
                          password='foobarham')
        self.torrent = factories.TorrentFactory()

    def test_no_perms(self):
        user = factories.UserFactory.create(is_staff=False, is_superuser=False)
        self.client.login(username=user.username,
                          password='foobarham')
        url = self.torrent.get_start_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_not_exists(self):
        url = self.torrent.get_start_url()
        self.torrent.delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch('dj_torrent.models.TorrentManager.client')
    def test_stop(self, tr_mock):
        url = self.torrent.get_stop_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        tr_mock.stop_torrent.assert_called

    @patch('dj_torrent.models.TorrentManager.client')
    def test_start(self, tr_mock):
        url = self.torrent.get_start_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        tr_mock.stop_torrent.assert_called

    @patch('dj_torrent.models.TorrentManager.client')
    def test_remove(self, tr_mock):
        url = self.torrent.get_remove_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        tr_mock.stop_torrent.assert_called
