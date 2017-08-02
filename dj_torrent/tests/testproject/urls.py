from django.conf.urls import url, include
from django.contrib import admin
from dj_torrent import urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('dj_torrent.urls')),
]
