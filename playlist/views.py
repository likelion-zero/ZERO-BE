from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from create.models import Song, SongDetail, Word, History, Playlist

User = get_user_model()


class PlaySongView(APIView):
    def get(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)

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

        history, _ = History.objects.get_or_create(
            song=song,
            defaults={"count": 0},
        )
        history.count += 1
        history.save()

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
        user = get_object_or_404(User, username=user_id)

        playlist_items = (
            Playlist.objects
            .filter(user=user)
            .select_related("song")
        )

        songs_data = []

        for item in playlist_items:
            song = item.song
            
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
                "history_count": history.count,
                "image_words": image_words,
            })

        return Response({
            "user_id": user.username,
            "songs": songs_data,
        })


class DeleteFromPlaylistView(APIView):
    def delete(self, request, user_id, song_id):
        user = get_object_or_404(User, username=user_id)

        playlist_item = get_object_or_404(
            Playlist,
            user=user,
            song_id=song_id
        )

        playlist_item.delete()

        return Response({
            "user_id": user.username,
            "song_id": song_id,
            "status": "deleted_from_playlist_only"
        })
