import random

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from create.models import Song, SongDetail, Word, History, Playlist

User = get_user_model()


class ChartView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, username=user_id)

        # 1) 이 유저가 만든 곡들 (is_creator=True)
        creator_song_ids_qs = Playlist.objects.filter(
            user=user,
            is_creator=True,
        ).values_list("song_id", flat=True)

        creator_song_ids = list(creator_song_ids_qs)

        # 🔹 (A) 이 유저가 만든 곡이 하나도 없는 경우 → 전역 top3 추천 모드
        if not creator_song_ids:
            songs_data = self._get_global_top3_songs_excluding_user(user)
            return Response({
                "user_id": user.username,
                "base_word": None,
                "songs": songs_data,
            })

        # 🔹 (B) 이 유저가 만든 곡은 있지만, 그 안에서 base_word 뽑아서 추천하는 모드

        # 2) 그 곡들에 속한 Word 중에서 랜덤 1개 선택 (base_word)
        user_words_qs = Word.objects.filter(
            song_id__in=creator_song_ids
        ).values_list("word", flat=True).distinct()

        user_words = list(user_words_qs)

        # 만약 단어도 하나도 없으면 → 전역 top3 로 fallback
        if not user_words:
            songs_data = self._get_global_top3_songs_excluding_user(user)
            return Response({
                "user_id": user.username,
                "base_word": None,
                "songs": songs_data,
            })

        base_word = random.choice(user_words)

        # 3) base_word 가 들어간 모든 song_id
        song_ids_with_word = Word.objects.filter(
            word=base_word
        ).values_list("song_id", flat=True).distinct()

        # 4) 그 song_id 중에서 "남이 만든 곡"만 대상으로
        creator_playlists = Playlist.objects.filter(
            song_id__in=song_ids_with_word,
            is_creator=True
        ).select_related("user", "song")

        candidates = []  # (song, creator_username, history_count)

        for pl in creator_playlists:
            # 본인이 만든 곡은 제외
            if pl.user_id == user.id:
                continue

            song = pl.song
            creator_username = pl.user.username

            history, _ = History.objects.get_or_create(
                song=song,
                defaults={"count": 0}
            )

            candidates.append((song, creator_username, history.count))

        # history 상위 3개
        candidates.sort(key=lambda x: x[2], reverse=True)
        top3 = candidates[:3]

        songs_data = self._build_song_response_list(top3)

        return Response({
            "user_id": user.username,
            "base_word": base_word,
            "songs": songs_data,
        })

    # ----------------- 헬퍼 함수들 -----------------

    def _get_global_top3_songs_excluding_user(self, user):
        """
        이 유저가 만든 곡이 하나도 없거나,
        base_word 를 뽑을 수 없을 때 사용하는 전역 TOP3 추천
        """
        songs_with_history = (
            History.objects
            .select_related("song")
            .order_by("-count")
        )

        candidates = []  # (song, creator_username, history_count)

        for h in songs_with_history:
            song = h.song

            # 이 곡의 생성자 찾기 (있을 수도 있고 없을 수도 있음)
            creator_pl = Playlist.objects.filter(
                song=song,
                is_creator=True
            ).select_related("user").first()

            # 생성자가 이 유저라면 제외 (일반 조건)
            if creator_pl and creator_pl.user_id == user.id:
                continue

            creator_username = creator_pl.user.username if creator_pl else None

            candidates.append((song, creator_username, h.count))

            if len(candidates) >= 3:
                break

        return self._build_song_response_list(candidates)

    def _build_song_response_list(self, song_creator_history_triplets):
        """
        (song, creator_username, history_count) 리스트를
        최종 응답용 dict 리스트로 변환
        """
        songs_data = []

        for song, creator_username, history_count in song_creator_history_triplets:
            detail = (
                SongDetail.objects
                .filter(song=song)
                .order_by("-id")
                .first()
            )

            image_words = list(
                Word.objects
                .filter(song=song)
                .values_list("word", flat=True)[:9]
            )

            songs_data.append({
                "song_id": song.id,
                "title": song.title,
                "language": song.language,
                "genre": song.genre,
                "mood": song.mood,
                "runtime": detail.runtime if detail else None,
                "created_by": creator_username,
                "history_count": history_count,
                "image_words": image_words,
            })

        return songs_data
