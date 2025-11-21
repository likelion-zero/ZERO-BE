from rest_framework import serializers
from create.models import Song


class ChartSongSerializer(serializers.ModelSerializer):
    song_id = serializers.IntegerField(source="pk")
    created_by = serializers.CharField(source="create_user.username")
    runtime = serializers.SerializerMethodField()
    history_count = serializers.SerializerMethodField()
    image_words = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            "song_id",
            "title",
            "language",
            "genre",
            "mood",
            "runtime",
            "created_by",
            "history_count",
            "image_words",
        ]

    def get_runtime(self, obj):
        detail = getattr(obj, "songdetail", None)
        return detail.runtime if detail else None

    def get_history_count(self, obj):
        history = getattr(obj, "history", None)
        return history.count if history else 0

    def get_image_words(self, obj):
        qs = obj.words.all().order_by("id")[:9]
        return [w.word for w in qs]
