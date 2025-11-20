from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from create.models import Song, Playlist, History
from .serializers import PlaylistSongSerializer, SongPlaySerializer

User = get_user_model()


class PlaylistListView(APIView):
    permission_classes = [permissions.AllowAny]  # 인증 붙일 거면 수정

    def get(self, request, user_id):
        user = get_object_or_404(User, username=user_id)
        qs = Playlist.objects.filter(user=user).select_related(
            'song',
            'song__detail',
            'song__history',
            'song__create_user',
        )
        serializer = PlaylistSongSerializer(qs, many=True)
        return Response({"user_id": user.username, "songs": serializer.data})


class PlaylistDeleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, user_id, song_id):
        user = get_object_or_404(User, username=user_id)
        playlist_item = get_object_or_404(
            Playlist,
            user=user,
            song__pk=song_id,
        )
        playlist_item.delete()
        return Response(
            {
                "user_id": user.username,
                "song_id": song_id,
                "status": "deleted_from_playlist_only",
            },
            status=status.HTTP_200_OK,
        )


class SongPlayView(APIView):
    """
    GET  : 곡 정보 조회 (history 그대로)
    POST : 실제 재생 시점에 history_count +1
    """

    permission_classes = [permissions.AllowAny]

    def get_object(self, song_id):
        return get_object_or_404(Song.objects.select_related(
            'detail', 'history', 'create_user'
        ), pk=song_id)

    def get(self, request, song_id):
        song = self.get_object(song_id)
        serializer = SongPlaySerializer(song)
        return Response(serializer.data)

    def post(self, request, song_id):
        song = self.get_object(song_id)

        history, _ = History.objects.get_or_create(song=song)
        history.count += 1
        history.save()

        serializer = SongPlaySerializer(song)
        # updated_history_count만 필요하면 serializer 대신 값만 보내도 됨
        return Response(serializer.data, status=status.HTTP_200_OK)
