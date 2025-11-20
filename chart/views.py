import random
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from create.models import Song, Word
from .serializers import ChartSongSerializer

User = get_user_model()


class ChartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, username=user_id)

        # 1) 유저가 입력했던 단어들
        user_words_qs = Word.objects.filter(create_user=user)
        words_list = list(user_words_qs.values_list('word', flat=True).distinct())

        if not words_list:
            return Response(
                {"user_id": user.username, "base_word": None, "songs": []}
            )

        # 2) 랜덤 단어 선택
        base_word = random.choice(words_list)

        # 3) 그 단어가 포함된 곡들
        song_ids = Word.objects.filter(word=base_word).values_list('song_id', flat=True)

        songs_qs = (
            Song.objects.filter(pk__in=song_ids)
            .select_related('detail', 'history', 'create_user')
            .order_by('-history__count')[:3]
        )

        serializer = ChartSongSerializer(songs_qs, many=True)

        return Response(
            {
                "user_id": user.username,
                "base_word": base_word,
                "songs": serializer.data,
            }
        )

