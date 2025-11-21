from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Song, SongDetail, Word, History

User = get_user_model()


class SongCreateSerializer(serializers.Serializer):
    # create 화면에서 받는 값
    title = serializers.CharField(max_length=200)
    language = serializers.CharField(max_length=20)
    genre = serializers.CharField(max_length=50)
    mood = serializers.CharField(max_length=50)
    words = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False,
    )

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user if request.user.is_authenticated else None

        words = validated_data.pop("words")
        song = Song.objects.create(create_user=user, **validated_data)

        # word 저장
        word_objs = [
            Word(song=song, create_user=user, word=w)
            for w in words
        ]
        Word.objects.bulk_create(word_objs)

        # history 0으로 생성
        History.objects.create(song=song, count=0)

        return song

    def to_representation(self, instance: Song):
        # 응답 구조
        return {
            "song_id": instance.pk,
            "title": instance.title,
            "language": instance.language,
            "genre": instance.genre,
            "mood": instance.mood,
            "created_by": instance.create_user.username if instance.create_user else None,
            "words": list(instance.words.values_list("word", flat=True)),
        }


class MeaningResponseSerializer(serializers.Serializer):
    word = serializers.CharField()
    source_language = serializers.CharField()
    target_language = serializers.CharField()
    meanings = serializers.ListField(child=serializers.CharField())


class SongGenerateRequestSerializer(serializers.Serializer):
    duration_sec = serializers.IntegerField(required=False, default=60)
    model = serializers.CharField(required=False, default="suno_v3_5")
    extra_prompt = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SongDetailSerializer(serializers.ModelSerializer):
    song_id = serializers.IntegerField(source="song.pk")
    title = serializers.CharField(source="song.title")
    language = serializers.CharField(source="song.language")
    genre = serializers.CharField(source="song.genre")
    mood = serializers.CharField(source="song.mood")
    created_by = serializers.CharField(source="song.create_user.username", allow_null=True)
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
            "audio_url",
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
        # 상위 9개만
        qs = obj.song.words.all().order_by("id")[:9]
        return [w.word for w in qs]
