from django.contrib import admin
from .models import Song, SongDetail, Word, History, Playlist

admin.site.register(Song)
admin.site.register(SongDetail)
admin.site.register(Word)
admin.site.register(History)
admin.site.register(Playlist)
