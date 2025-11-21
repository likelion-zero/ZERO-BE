from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from create.models import Song, SongDetail, Word, History


class PlaySongView(APIView):
    def get(self, request, song_id):
        # 1) 곡 기본 정보
        song = get_object_or_404(Song, id=song_id)

        # 2) 곡 상세 정보 (가장 최신 한 개 사용)
        detail = (
            SongDetail.objects
            .filter(song=song)
            .order_by("-id")
            .first()
        )

        # 3) image_words : 해당 곡의 Word에서 상위 9개
        image_words_qs = (
            Word.objects
            .filter(song=song)
            .values_list("word", flat=True)[:9]
        )
        image_words = list(image_words_qs)

        # 4) history_count : History 테이블에서 조회
        history, _ = History.objects.get_or_create(
            song=song,
            defaults={"count": 0},
        )

        history.count += 1
        history.save()

        # 5) 응답 JSON 만들기
        data = {
            "song_id": song.id,
            "title": song.title,
            "genre": song.genre,
            "mood": song.mood,
            "runtime": detail.runtime if detail else None,
            "audio_url": detail.song_url if detail else None,
            "lyrics": detail.lyrics if detail else "",
            "image_words": image_words,
            "history_count": history.count,
        }

        return Response(data)
