from rest_framework import serializers
from create.models import Playlist, Song, SongDetail, History


class PlaylistSongSerializer(serializers.ModelSerializer):
    song_id = serializers.IntegerField(source="song.pk")
    title = serializers.CharField(source="song.title")
    language = serializers.CharField(source="song.language")
    genre = serializers.CharField(source="song.genre")
    mood = serializers.CharField(source="song.mood")
    created_by = serializers.CharField(source="song.create_user.username")

    history_count = serializers.SerializerMethodField()
    image_words = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = [
            "song_id",
            "title",
            "language",
            "genre",
            "mood",
            "created_by",
            "song_title",
            "history_count",
            "image_words",
        ]

    def get_history_count(self, obj):
        history = getattr(obj.song, "history", None)
        return history.count if history else 0

    def get_image_words(self, obj):
        qs = obj.song.words.all().order_by("id")[:9]
        return [w.word for w in qs]


class SongPlaySerializer(serializers.ModelSerializer):
    song_id = serializers.IntegerField(source="song.pk")
    title = serializers.CharField(source="song.title")
    language = serializers.CharField(source="song.language")
    genre = serializers.CharField(source="song.genre")
    mood = serializers.CharField(source="song.mood")
    created_by = serializers.CharField(source="song.create_user.username")

    history_count = serializers.SerializerMethodField()
    words = serializers.SerializerMethodField()
    image_words = serializers.SerializerMethodField()

    class Meta:
        model = SongDetail
        fields = [
            "song_id",
            "title",
            "language",
            "genre",
            "mood",
            "created_by",
            "runtime",
            "song_url",
            "lyrics",
            "keywords",
            "words",
            "image_words",
            "history_count",
        ]

    def get_history_count(self, obj):
        history = getattr(obj.song, "history", None)
        return history.count if history else 0

    def get_words(self, obj):
        return list(obj.song.words.values_list("word", flat=True))

    def get_image_words(self, obj):
        qs = obj.song.words.all().order_by("id")[:9]
        return [w.word for w in qs]
