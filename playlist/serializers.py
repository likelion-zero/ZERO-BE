from rest_framework import serializers
from django.contrib.auth import get_user_model
from create.models import Song, SongDetail, Word, History, Playlist

User = get_user_model()


def get_image_words_for_song(song, limit=9):
    qs = Word.objects.filter(song=song).order_by('id')[:limit]
    return [w.word for w in qs]


class PlaylistSongSerializer(serializers.ModelSerializer):
    # Song 기본 정보
    song_id = serializers.IntegerField(source='song.pk')
    title = serializers.CharField(source='song.title')
    language = serializers.CharField(source='song.language')
    genre = serializers.CharField(source='song.genre')
    mood = serializers.CharField(source='song.mood')
    created_by = serializers.CharField(source='song.create_user.username')

    # SongDetail
    runtime = serializers.IntegerField(source='song.detail.runtime', read_only=True)

    # History
    history_count = serializers.SerializerMethodField()

    # 자켓용 단어 9개
    image_words = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = [
            'song_id',
            'title',
            'language',
            'genre',
            'mood',
            'runtime',
            'created_by',
            'is_from_chart',
            'history_count',
            'last_played_at',
            'image_words',
        ]

    def get_history_count(self, obj):
        history = getattr(obj.song, 'history', None)
        return history.count if history else 0

    def get_image_words(self, obj):
        return get_image_words_for_song(obj.song)


class SongPlaySerializer(serializers.ModelSerializer):
    # Song 기본 정보
    song_id = serializers.IntegerField(source='pk')
    created_by = serializers.CharField(source='create_user.username')

    # SongDetail
    runtime = serializers.IntegerField(source='detail.runtime', read_only=True)
    audio_url = serializers.CharField(source='detail.audio_url', read_only=True)
    lyrics = serializers.CharField(source='detail.lyrics', read_only=True)

    # History
    history_count = serializers.SerializerMethodField()

    # 전체 단어 / 자켓용 단어
    words = serializers.SerializerMethodField()
    image_words = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            'song_id',
            'title',
            'language',
            'genre',
            'mood',
            'created_by',
            'runtime',
            'audio_url',
            'lyrics',
            'words',
            'image_words',
            'history_count',
        ]

    def get_history_count(self, obj):
        history = getattr(obj, 'history', None)
        return history.count if history else 0

    def get_words(self, obj):
        return list(obj.words.values_list('word', flat=True))

    def get_image_words(self, obj):
        return get_image_words_for_song(obj)
