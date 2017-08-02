"""
Models for the Torrent app.
"""
from datetime import timedelta, datetime
import os
import re
import logging

from django.db import models
try:
    from django.urls import reverse
except ImportError:
    # Django 1.0
    from django.core.urlresolvers import reverse

import transmissionrpc
import dateutil.tz

from dj_torrent import settings


class TorrentManager(models.Manager):
    """Manager class for the `Torrent` objects.
    """
    _client = None

    @property
    def client(self):
        if not self._client:
            try:
                self._client = transmissionrpc.Client(
                    address=settings.TRANSMISSION_HOST,
                    port=settings.TRANSMISSION_PORT,
                    user=settings.TRANSMISSION_USER,
                    password=settings.TRANSMISSION_PASS
                )
            except transmissionrpc.TransmissionError as e:
                logging.exception(e)
                pass
        return self._client

    def get_or_create_from_torrentrpc(self, torrent):
        obj, created = self.get_or_create(hash=torrent.hashString)
        dirty = False
        if obj.name != torrent.name:
            obj.name = torrent.name
            dirty = True
        d = torrent.date_added
        # Offset back to UTC
        if d.tzinfo:
            d = d.astimezone(dateutil.tz.tzutc())
        else:
            d = d.replace(tzinfo=dateutil.tz.tzutc())
        if not settings.USE_TZ:
            d = d.replace(tzinfo=None)
        if obj.date_added != d:
            obj.date_added = d
            dirty = True
        if obj.base_id != torrent.id:
            obj.base_id = torrent.id
            dirty = True
        if obj.status != torrent.status:
            obj.status = torrent.status
            dirty = True
        if abs(obj.progress - torrent.progress) > 0.0001:
            obj.progress = torrent.progress
            dirty = True

        if obj.progress == 100.0 and obj.status in ['stopped', 'seeding']:
            download_dir = obj.download_dir().rstrip(os.sep)
            for d in settings.TORRENT_DIRS:
                if d[1] != download_dir:
                    # These are not the droids you are looking for, move along
                    continue
                if len(d) > 3:
                    secs = d[3]
                    now = datetime.now()
                    if obj.base().date_done + timedelta(seconds=secs) < now:
                        # Past the expiration date
                        logging.info('%s has expired, removing', obj)
                        result = self.client.remove_torrent(obj.base_id)
                        logging.info('Result: %s', result)
                        obj.deleted = True
                        obj.base_id = -1
                        dirty = True
                        break
                if len(d) > 2:
                    secs = d[2]
                    now = datetime.now()
                    if obj.base().date_done + timedelta(seconds=secs) < now:
                        # Past the expiration date
                        if not obj.deleted:
                            logging.info('%s has expired, ignoring', obj)
                            obj.deleted = True
                            dirty = True
                            break
        elif obj.deleted:
            obj.deleted = False
            dirty = True

        if dirty:
            logging.info('Updating %s', obj)
            obj.save()
        return obj, created

    def sync(self):
        hashes = []
        for torrent in self.client.get_torrents():
            logging.debug('Processiong %s', torrent)
            obj, craeted = self.get_or_create_from_torrentrpc(torrent)
            if not obj.deleted:
                hashes.append(torrent.hashString)
        qs = self.exclude(hash__in=hashes).exclude(deleted=True)
        updated = qs.update(deleted=True, base_id=-1)
        if updated > 0:
            logging.info('Removed %d torrent(s)', updated)

    def active(self):
        qs = super(TorrentManager, self).get_queryset()
        return qs.filter(deleted=False)


class Torrent(models.Model):
    """Proxy object for transmissionrpc's Torrent object.
    """
    base_id = models.IntegerField(default=-1)
    hash = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='')
    progress = models.FloatField(default=0.0)
    date_added = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    owners = models.ManyToManyField('auth.User', blank=True)
    objects = TorrentManager()

    class Meta:
        app_label = 'dj_torrent'
        ordering = ['-date_added']

    def __unicode__(self):
        return '%d: %s, %s, %s' % (
            self.base_id, self.name, self.hash, self.owners.all())

    def get_absolute_url(self):
        return reverse('torrent_torrent_detail', kwargs={'id': self.base_id})

    def get_start_url(self):
        return reverse('torrent_torrent_action', kwargs={
            'id': self.base_id,
            'action': 'start',
            'hash': self.hash,
        })

    def get_stop_url(self):
        return reverse('torrent_torrent_action', kwargs={
            'id': self.base_id,
            'action': 'stop',
            'hash': self.hash,
        })

    def get_add_url(self):
        return reverse('torrent_torrent_action', kwargs={
            'id': self.base_id,
            'action': 'add',
            'hash': self.hash,
        })

    def get_remove_url(self):
        return reverse('torrent_torrent_action', kwargs={
            'id': self.base_id,
            'action': 'remove',
            'hash': self.hash,
        })

    def progress_css_class(self):
        if self.status == 'downloading':
            return 'progress-striped active'
        if self.status == 'seeding':
            return 'progress-success'
        if self.status == 'stopped':
            return 'progress-disabled'
        return ''

    def fields(self):
        return self.base()._fields

    def base(self):
        return Torrent.objects.client.get_torrent(self.base_id)

    def download_dir(self):
        return self.fields()['downloadDir'].value

    def file_url(self):
        return '/'.join([
            re.sub(
                settings.TRANSMISSION_DOWNLOAD_ROOT.rstrip(os.sep),
                settings.TRANSMISSION_DOWNLOAD_URL.rstrip('/'),
                self.download_dir()
            ).replace('\\', '/'),
            self.name
        ])
