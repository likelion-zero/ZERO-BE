# chart/serializers.py
from rest_framework import serializers
from create.models import Song, Word, History
from playlist.serializers import get_image_words_for_song  # 공용 함수 재사용


class ChartSongSerializer(serializers.ModelSerializer):
    song_id = serializers.IntegerField(source='pk')
    runtime = serializers.IntegerField(source='detail.runtime', read_only=True)
    created_by = serializers.CharField(source='create_user.username')
    history_count = serializers.SerializerMethodField()
    image_words = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            'song_id',
            'title',
            'language',
            'genre',
            'mood',
            'runtime',
            'created_by',
            'history_count',
            'image_words',
        ]

    def get_history_count(self, obj):
        history = getattr(obj, 'history', None)
        return history.count if history else 0

    def get_image_words(self, obj):
        return get_image_words_for_song(obj)
