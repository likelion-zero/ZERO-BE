import random
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from create.models import Song, Word
from .serializers import ChartSongSerializer

User = get_user_model()


class ChartView(APIView):
    """
    GET /api/chart/{username}
    1) 해당 유저가 입력한 Word 중 랜덤 한 단어 선택
    2) 그 단어를 가진 Song 중 History.count 높은 순 상위 3개
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)

        # 유저가 입력한 단어들
        user_words_qs = Word.objects.filter(create_user=user)
        distinct_words = list(user_words_qs.values_list("word", flat=True).distinct())

        if not distinct_words:
            return Response(
                {
                    "user_id": user.username,
                    "base_word": None,
                    "songs": [],
                }
            )

        base_word = random.choice(distinct_words)

        # 해당 단어가 포함된 곡들
        song_ids = Word.objects.filter(word=base_word).values_list("song_id", flat=True)

        songs_qs = (
            Song.objects.filter(pk__in=song_ids)
            .select_related("create_user", "songdetail", "history")
            .order_by("-history__count")
        )[:3]

        serializer = ChartSongSerializer(songs_qs, many=True)

        return Response(
            {
                "user_id": user.username,
                "base_word": base_word,
                "songs": serializer.data,
            }
        )
