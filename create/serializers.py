from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Song, Word, Playlist

User = get_user_model()


class SongCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    language = serializers.CharField()
    genre = serializers.CharField()
    mood = serializers.CharField()
    # created_by = serializers.CharField()
    words = serializers.ListField(child=serializers.CharField())
    meaning = serializers.ListField(child=serializers.CharField())

    def validate(self, attrs):
        if len(attrs["words"]) != len(attrs["meaning"]):
            raise serializers.ValidationError("words와 meaning 길이가 다릅니다.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # 로그인/회원 시스템이 없으므로, 실제 User 인스턴스가 아니면 None으로 처리
        if not isinstance(user, User) or not getattr(user, "is_authenticated", False):
            user = None

        # validated_data.pop("created_by", None)

        # username = validated_data.pop("created_by")
        words = validated_data.pop("words")
        meanings = validated_data.pop("meaning")

        # user = User.objects.get(username=username)

        # Song 생성 (User 없음)
        song = Song.objects.create(**validated_data)

        # Word 저장
        for w, m in zip(words, meanings):
            Word.objects.create(song=song, word=w, meaning=m)

        # Playlist 연결
        Playlist.objects.create(
            song=song,
            user=user,
            is_creator=True
        )

        return song