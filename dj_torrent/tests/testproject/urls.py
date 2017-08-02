from django.conf.urls import url
from django.contrib import admin
import dj_torrent

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^/', dj_torrent.urls),
]
