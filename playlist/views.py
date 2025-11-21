from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from create.models import Song, SongDetail, Word, History, Playlist


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

class UserPlaylistView(APIView):
    def get(self, request, user_id):
        # 1) user_id = username 으로 유저 찾기
        user = get_object_or_404(User, username=user_id)

        # 2) 해당 유저의 플레이리스트 항목들 (create.Playlist 사용)
        playlist_items = (
            Playlist.objects
            .filter(user=user)
            .select_related("song", "song__user")
        )

        songs_data = []

        for item in playlist_items:
            song = item.song

            # 3) SongDetail: 가장 최신 한 개 사용 (없으면 None)
            detail = (
                SongDetail.objects
                .filter(song=song)
                .order_by("-id")
                .first()
            )

            # 4) image_words: Word에서 상위 9개
            words_qs = (
                Word.objects
                .filter(song=song)
                .values_list("word", flat=True)[:9]
            )
            image_words = list(words_qs)

            # 5) history_count: History
            history, _ = History.objects.get_or_create(
                song=song,
                defaults={"count": 0},
            )

            songs_data.append({
                "song_id": song.id,
                "title": song.title,
                "language": song.language,
                "genre": song.genre,
                "mood": song.mood,
                "runtime": detail.runtime if detail else None,
                "created_by": song.user.username,
                "history_count": history.count,
                "image_words": image_words,
            })

        return Response({
            "user_id": user.username,
            "songs": songs_data,
        })
        