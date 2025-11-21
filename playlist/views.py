from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from create.models import Song, SongDetail, Playlist, History
from .serializers import PlaylistSongSerializer, SongPlaySerializer

User = get_user_model()


class PlaylistListView(APIView):
    """
    GET /api/playlist/{username}
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        qs = Playlist.objects.filter(user=user).select_related(
            "song",
            "song__create_user",
        )
        serializer = PlaylistSongSerializer(qs, many=True)
        return Response(
            {
                "user_id": user.username,
                "songs": serializer.data,
            }
        )


class PlaylistDeleteView(APIView):
    """
    DELETE /api/playlist/{username}/del/{song_id}
    """

    permission_classes = [permissions.AllowAny]

    def delete(self, request, username, song_id):
        user = get_object_or_404(User, username=username)
        playlist_item = get_object_or_404(
            Playlist,
            user=user,
            song__pk=song_id,
        )
        playlist_item.delete()
        return Response(
            {
                "user_id": user.username,
                "song_id": int(song_id),
                "status": "deleted_from_playlist_only",
            },
            status=status.HTTP_200_OK,
        )


class SongPlayView(APIView):
    """
    GET  /api/playlist/play/{song_id}  : 곡 상세 조회
    POST /api/playlist/play/{song_id}  : history_count + 1
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, song_id):
        song = get_object_or_404(Song, pk=song_id)
        detail = get_object_or_404(SongDetail, song=song)
        serializer = SongPlaySerializer(detail)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, song_id):
        song = get_object_or_404(Song, pk=song_id)
        history, _ = History.objects.get_or_create(song=song)
        history.count += 1
        history.save()

        return Response(
            {
                "song_id": song.pk,
                "updated_history_count": history.count,
            },
            status=status.HTTP_200_OK,
        )
