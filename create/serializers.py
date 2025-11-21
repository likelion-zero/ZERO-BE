from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Song, Word

User = get_user_model()


class SongCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    language = serializers.CharField()
    genre = serializers.CharField()
    mood = serializers.CharField()
    created_by = serializers.CharField()
    words = serializers.ListField(child=serializers.CharField())
    meaning = serializers.ListField(child=serializers.CharField())

    def validate(self, attrs):
        if len(attrs["words"]) != len(attrs["meaning"]):
            raise serializers.ValidationError("words와 meaning 길이가 다름")
        return attrs

    def create(self, validated_data):
        username = validated_data.pop("created_by")
        words = validated_data.pop("words")
        meanings = validated_data.pop("meaning")

        user = User.objects.get(username=username)

        # 1) Song 저장
        song = Song.objects.create(
            user=user,
            **validated_data
        )

        # 2) Word 여러 개 저장
        for w, m in zip(words, meanings):
            Word.objects.create(
                song=song,
                user=user,
                word=w,
                meaning=m,
            )

        return song