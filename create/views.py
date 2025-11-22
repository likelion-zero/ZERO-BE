from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SongCreateSerializer
from .models import Song, SongDetail, History
from create.api import (
    get_word_meanings,
    request_suno_generate,
)


class CreateSongView(APIView):
    def post(self, request):
        serializer = SongCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        song = serializer.save()

        return Response(
            {
                "success": True,
                "song_id": song.id,
                "message": "곡 정보가 저장되었습니다. 이제 Suno AI 요청을 보내세요.",
                "next_action": "CALL_SUNO",
            },
            status=status.HTTP_201_CREATED,
        )


class MeaningView(APIView):
    def get(self, request, word):
        meanings = get_word_meanings(word)

        return Response(
            {
                "word": word,
                "meanings": meanings,
            }
        )


class SunoGenerateView(APIView):
    """
    POST /api/create/{song_id}/

    - song_id 기준으로 Song + Word 정보를 조회
    - Suno API에 곡 생성 요청
    - Suno가 비동기로 콜백을 보내면 SongDetail + History 저장
    - 여기서는 taskId를 Song에 저장하고 Suno 응답을 그대로 반환
    """

    def post(self, request, song_id: int):
        # 1) song 조회
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response(
                {"detail": "해당 song_id의 곡을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # song과 연결된 단어들 (Word 모델에서 related_name='words' 라고 가정)
        words_qs = song.words.all()

        # 2) 요청 바디에 옵션이 있으면 Suno 옵션으로 사용
        extra_options = request.data if isinstance(request.data, dict) else {}

        # 3) Suno generate 호출
        try:
            generate_result = request_suno_generate(song, words_qs, extra_options)
        except Exception as e:
            return Response(
                {
                    "detail": "Suno API 호출 중 오류가 발생했습니다.",
                    "error": str(e),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # 4) taskId 추출 후 Song 에 저장
        task_id = None
        if isinstance(generate_result, dict):
            data_block = generate_result.get("data") or {}
            task_id = data_block.get("taskId")

        if task_id:
            song.suno_task_id = task_id  # Song 모델에 suno_task_id 필드가 있어야 함
            song.save(update_fields=["suno_task_id"])

        # 5) 클라이언트로 Suno 응답 그대로 반환
        return Response(generate_result, status=status.HTTP_201_CREATED)


class SunoCallbackView(APIView):
    """
    POST /api/create/callback/

    Suno API 가 곡 생성 완료 시 이 엔드포인트로 결과를 전송한다.

    예상 요청 예시:
    {
      "taskId": "bb3f83b9f9bcd49080f84609671c4c36",
      "status": "SUCCESS",
      "response": {
        "data": [
          {
            "id": "audio_123",
            "audio_url": "https://example.com/generated-music.mp3",
            "title": "Generated Song",
            "tags": "hiphop, chill",
            "duration": 180.5,
            "lyrics": "...."
          }
        ]
      }
    }
    """

    def post(self, request):
        data = request.data

        task_id = data.get("taskId")
        status_str = data.get("status")

        if not task_id:
            return Response(
                {"error": "taskId 가 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # taskId 로 Song 찾기
        try:
            song = Song.objects.get(suno_task_id=task_id)
        except Song.DoesNotExist:
            return Response(
                {"error": f"Unknown taskId: {task_id}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 성공인 경우에만 SongDetail / History 저장
        if status_str == "SUCCESS":
            try:
                response_block = data.get("response") or {}
                tracks = response_block.get("data") or []

                if tracks:
                    first_track = tracks[0]

                    audio_url = (
                        first_track.get("audio_url")
                        or first_track.get("audioUrl")
                        or ""
                    )
                    duration = first_track.get("duration") or 0
                    lyrics = first_track.get("lyrics") or ""

                    try:
                        duration_int = int(duration)
                    except (TypeError, ValueError):
                        duration_int = 0

                    # SongDetail 기록 (필드명은 실제 모델에 맞게 조정)
                    SongDetail.objects.create(
                        song=song,
                        song_url=audio_url,
                        runtime=duration_int,
                        lyrics=lyrics,
                    )

                    # History 초기값 생성 (없으면)
                    History.objects.get_or_create(song=song, defaults={"count": 0})

            except Exception as e:
                return Response(
                    {"error": f"callback 처리 중 오류: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response({"success": True}, status=status.HTTP_200_OK)
