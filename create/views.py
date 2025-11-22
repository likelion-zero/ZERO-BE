from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SongCreateSerializer
from .models import Song, SongDetail, History
from create.api import (
    get_word_meanings,
    request_suno_generate,
    request_suno_task_status,
)


class CreateSongView(APIView):
    def post(self, request):
        # serializer = SongCreateSerializer(data=request.data)
        serializer = SongCreateSerializer(
            data=request.data,
            context={"request": request},
        )


        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        song = serializer.save()

        return Response(
            {
                "success": True,
                "song_id": song.id,
                "message": "곡 정보가 저장되었습니다. 이제 Suno AI 요청을 보내세요.",
                "next_action": "CALL_SUNO"
            },
            status=status.HTTP_201_CREATED
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
    - task 상태를 한 번 조회해서 결과를 받으면
      SongDetail + History 초기값을 저장
    - Suno 응답(JSON)을 그대로 클라이언트에 반환
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

        # song과 연결된 단어들
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

        # generate_result 예시: {"code":200,"msg":"success","data":{"taskId":"..."}}
        task_id = None
        if isinstance(generate_result, dict):
            task_id = (generate_result.get("data") or {}).get("taskId")

        # 4) task_id 가 있으면 상태 조회 시도
        final_result = generate_result
        if task_id:
            try:
                status_result = request_suno_task_status(task_id)
                # 상태 조회가 성공하면 그 결과를 최종 응답으로 사용
                final_result = status_result
            except Exception:
                # 상태 조회 실패 시에는 처음 generate 결과만 반환
                pass

        # 5) 상태 조회 결과를 기반으로 SongDetail + History 저장 시도
        try:
            data_block = final_result.get("data") or {}
            status_str = data_block.get("status")
            if status_str == "SUCCESS":
                response_block = data_block.get("response") or {}
                tracks = response_block.get("data") or []
                if tracks:
                    first_track = tracks[0]

                    audio_url = first_track.get("audio_url", "")
                    duration = first_track.get("duration", 0)
                    # Suno 응답에 가사는 없을 수 있으므로 일단 빈 문자열
                    lyrics = first_track.get("lyrics", "") or ""

                    # SongDetail 저장
                    SongDetail.objects.create(
                        song=song,
                        song_url=audio_url,
                        runtime=int(duration) if isinstance(duration, (int, float)) else 0,
                        lyrics=lyrics,
                    )

                    # History 초기값(없으면 생성, 있으면 그대로 사용)
                    History.objects.get_or_create(song=song, defaults={"count": 0})
        except Exception:
            # DB 저장 과정에서 에러가 나더라도
            # 클라이언트 응답까지 막지는 않음
            pass

        # 6) 클라이언트로 Suno 응답 그대로 반환
        return Response(final_result, status=status.HTTP_201_CREATED)