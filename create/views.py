from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Song, SongDetail
from .serializers import (
    SongCreateSerializer,
    MeaningResponseSerializer,
    SongGenerateRequestSerializer,
    SongDetailSerializer,
)
from .utils import translate_word_with_google, SunoClient


class SongCreateView(APIView):
    """
    POST /api/create
    곡 기본 정보 + 단어 리스트를 받아 Song, Word, History 생성
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SongCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        song = serializer.save()
        return Response(serializer.to_representation(song), status=status.HTTP_201_CREATED)


class WordMeaningView(APIView):
    """
    GET /api/create/meaning/{word}
    구글 번역 API(더미)로 단어 뜻 후보 반환
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, word):
        source_lang = request.query_params.get("source", "auto")
        target_lang = request.query_params.get("target", "ko")

        meanings = translate_word_with_google(word, source_lang, target_lang)

        serializer = MeaningResponseSerializer(
            {
                "word": word,
                "source_language": source_lang,
                "target_language": target_lang,
                "meanings": meanings,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SongGenerateView(APIView):
    """
    POST /api/create/{song_id}
    Suno AI(더미) 호출 → SongDetail 생성/업데이트 후 상세 정보 반환
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, song_id):
        song = get_object_or_404(Song, pk=song_id)

        req_serializer = SongGenerateRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        data = req_serializer.validated_data

        client = SunoClient(api_key=None)
        result = client.generate_song(
            song,
            duration_sec=data.get("duration_sec", 60),
            model=data.get("model", "suno_v3_5"),
            extra_prompt=data.get("extra_prompt"),
        )

        detail, _ = SongDetail.objects.update_or_create(
            song=song,
            defaults={
                "create_user": song.create_user,
                "song_url": result["song_url"],
                "runtime": result["runtime"],
                "lyrics": result["lyrics"],
                "keywords": result.get("keywords", []),
            },
        )

        res_serializer = SongDetailSerializer(detail)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)
