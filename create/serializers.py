from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Song, Word

User = get_user_model()


class SongSerializer(serializers.ModelSerializer):
    """
    곡 생성 + 단어 리스트를 한 번에 처리하는 Serializer

    - 입력:
        title, language, genre, mood, words(list[str])
        (로그인 유저 기준이면 created_by는 body에 안 보내도 됨)
    - 처리:
        Song 생성 후 Word 여러 개 생성
    - 출력:
        song_id, title, language, genre, mood, created_by(username), words(list[str])
    """

    # 입력용 words (필수 리스트)
    words = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True
    )

    # 출력용 created_by (Song.create_user.username)
    created_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Song
        fields = [
            "song_id",
            "title",
            "language",
            "genre",
            "mood",
            "created_by",  # read-only
            "words",       # write-only + 커스텀 rep에서 다시 채움
        ]
        read_only_fields = ["song_id", "created_by"]

    def get_created_by(self, obj):
        # Song.create_user 가 항상 존재한다고 가정
        return obj.create_user.username if obj.create_user_id else None

    def create(self, validated_data):
        # words 리스트 분리
        words_data = validated_data.pop("words", [])

        request = self.context.get("request")
        user = getattr(request, "user", None)

        # 1️⃣ 인증된 유저가 있으면 토큰에서 username 사용
        if user is not None and user.is_authenticated:
            create_user = user
        else:
            # 2️⃣ 인증이 없다면 body 에서 created_by(username) 사용 (선택)
            username = self.initial_data.get("created_by")
            if not username:
                raise serializers.ValidationError(
                    {"created_by": "인증 정보가 없거나 created_by가 전달되지 않았습니다."}
                )
            try:
                create_user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"created_by": "존재하지 않는 사용자입니다."}
                )

        # Song 생성 (create_user FK 사용)
        song = Song.objects.create(create_user=create_user, **validated_data)

        # Word 여러 개 생성 (song + create_user + word 문자열)
        word_objects = [
            Word(song=song, create_user=create_user, word=word_str)
            for word_str in words_data
        ]
        Word.objects.bulk_create(word_objects)

        return song

    def to_representation(self, instance):
        """
        응답 형식을 API 명세에 맞게 커스텀:
        - words: [ "focus", "motivation", ... ]
        """
        data = super().to_representation(instance)
        # related_name="words" 로 연결된 Word 객체들을 문자열 리스트로 변환
        data["words"] = [word.word for word in instance.words.all()]
        return data
