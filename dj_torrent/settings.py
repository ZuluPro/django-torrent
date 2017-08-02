import os
from django.conf import settings


TRANSMISSION_HOST = getattr(settings, 'TRANSMISSION_HOST', 'localhost')
TRANSMISSION_PORT = getattr(settings, 'TRANSMISSION_PORT', '9091')
TRANSMISSION_USER = getattr(settings, 'TRANSMISSION_USER', None)
TRANSMISSION_PASS = getattr(settings, 'TRANSMISSION_PASS', None)
TRANSMISSION_DOWNLOAD_ROOT = getattr(settings, 'TRANSMISSION_DOWNLOAD_ROOT',
                                     settings.MEDIA_ROOT)
TRANSMISSION_DOWNLOAD_URL = getattr(settings, 'TRANSMISSION_DOWNLOAD_URL',
                                    settings.MEDIA_URL)

DEFAULT_DIR = os.path.join(TRANSMISSION_DOWNLOAD_ROOT, 'downloads')
_DEFAULT_DIRS = [
    ('music', os.path.join(TRANSMISSION_DOWNLOAD_ROOT, 'music')),
    ('movie', os.path.join(TRANSMISSION_DOWNLOAD_ROOT, 'movies')),
    ('tv', os.path.join(TRANSMISSION_DOWNLOAD_ROOT, 'tv')),
    ('ebooks', os.path.join(TRANSMISSION_DOWNLOAD_ROOT, 'ebooks')),
    ('ebook', os.path.join(TRANSMISSION_DOWNLOAD_ROOT, 'ebooks')),
]
TORRENT_DIRS = getattr(settings, 'TORRENT_DIRS', [])
TORRENT_DIRS += _DEFAULT_DIRS
