import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "dj_torrent.tests.testproject.settings")
application = get_wsgi_application()
