from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Song, SongDetail, Word, History

User = get_user_model()


class SongCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    language = serializers.CharField(max_length=20)
    genre = serializers.CharField(max_length=50)
    mood = serializers.CharField(max_length=50)
    words = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False,
    )
    created_by = serializers.CharField(max_length=150, write_only=True)

    def create(self, validated_data):
        # created_by(username) → User 찾기
        username = validated_data.pop("created_by")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"created_by": "해당 username을 가진 유저가 없습니다."}
            )

        words = validated_data.pop("words")

        # Song 생성
        song = Song.objects.create(create_user=user, **validated_data)

        # Word 생성
        Word.objects.bulk_create(
            [Word(song=song, create_user=user, word=w) for w in words]
        )

        # History 초기화
        History.objects.create(song=song, count=0)

        return song

    def to_representation(self, instance: Song):
        # 응답 JSON
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
    extra_prompt = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )


class SongDetailSerializer(serializers.ModelSerializer):
    # SongDetail + Song + Word + History 합쳐서 응답용
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
