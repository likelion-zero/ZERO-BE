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






class SunoCallbackView(APIView):
    """
    POST /api/create/callback/

    Suno API가 곡 생성 완료 시 이 엔드포인트로 결과를 전송합니다.
    task_id로 Song을 찾아서 SongDetail과 History를 저장합니다.
    """

    def post(self, request):
        try:
            data = request.data

            # Suno API 콜백 데이터 구조에 따라 파싱
            task_id = data.get("taskId")
            status_str = data.get("status")

            if not task_id:
                return Response(
                    {"error": "taskId가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # task_id로 Song 찾기
            try:
                song = Song.objects.get(task_id=task_id)
            except Song.DoesNotExist:
                return Response(
                    {"error": f"task_id '{task_id}'에 해당하는 곡을 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 곡 생성이 성공한 경우에만 DB 저장
            if status_str == "SUCCESS":
                response_block = data.get("response") or {}
                tracks = response_block.get("data") or []

                if tracks:
                    first_track = tracks[0]

                    audio_url = first_track.get("audio_url", "")
                    duration = first_track.get("duration", 0)
                    lyrics = first_track.get("lyric", "") or first_track.get("lyrics", "") or ""

                    # 이미 SongDetail이 있는지 확인 (중복 방지)
                    existing_detail = SongDetail.objects.filter(song=song).first()

                    if not existing_detail:
                        # SongDetail 저장
                        SongDetail.objects.create(
                            song=song,
                            song_url=audio_url,
                            runtime=int(duration) if isinstance(duration, (int, float)) else 0,
                            lyrics=lyrics,
                        )

                        # History 초기값 생성
                        History.objects.get_or_create(song=song, defaults={"count": 0})

                    return Response(
                        {
                            "success": True,
                            "message": "곡 정보가 성공적으로 저장되었습니다.",
                            "song_id": song.id
                        },
                        status=status.HTTP_200_OK
                    )

            # SUCCESS가 아닌 경우 (PENDING, FAILED 등)
            return Response(
                {
                    "success": False,
                    "message": f"곡 생성 상태: {status_str}",
                    "task_id": task_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"콜백 처리 중 오류 발생: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

        # 4) task_id를 Song 모델에 저장
        if task_id:
            song.task_id = task_id
            song.save()

        # 5) 클라이언트로 Suno 응답 그대로 반환
        # 실제 곡 생성은 비동기로 처리되며, 완료되면 콜백으로 DB에 저장됨
        return Response(generate_result, status=status.HTTP_201_CREATED)