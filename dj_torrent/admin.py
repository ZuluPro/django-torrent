from django.contrib import admin
from . import models


@admin.register(models.Torrent)
class TorrentAdmin(admin.ModelAdmin):
    list_display = ('name', 'hash', 'progress', 'deleted')
    list_filter = ('status', 'date_added', 'deleted',)
    date_hierarchy = 'date_added'
    readonly_fields = ('hash', 'progress', 'date_added')
    search_fields = ('name', 'hash')
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'base_id', 'hash'),
            )
        }),
        ('Advanced options', {
            'fields': (
                ('date_added', 'status', 'progress', 'deleted'),
                'owners',
            ),
        }),
    )
