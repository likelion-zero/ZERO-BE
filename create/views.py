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
    곡 기본 정보 + 단어 리스트를 받아서 Song, Word, History 생성
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
    구글 번역 API를 통해 뜻 리스트 반환 (지금은 더미)
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, word):
        # 실제 구현에선 source/target을 query param으로 받을 수도 있음
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
    Suno AI 호출해서 SongDetail 생성 (지금은 더미)
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, song_id):
        song = get_object_or_404(Song, pk=song_id)

        req_serializer = SongGenerateRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        data = req_serializer.validated_data

        client = SunoClient(api_key=None)  # 실제 구현 시 설정에서 가져오기
        result = client.generate_song(
            song,
            duration_sec=data.get("duration_sec", 60),
            model=data.get("model", "suno_v3_5"),
            extra_prompt=data.get("extra_prompt"),
        )

        # SongDetail 생성 또는 업데이트
        detail, _ = SongDetail.objects.update_or_create(
            song=song,
            defaults={
                "runtime": result["runtime"],
                "audio_url": result["audio_url"],
                "lyrics": result["lyrics"],
                "keywords": result.get("keywords", ""),
            },
        )

        res_serializer = SongDetailSerializer(detail)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)
