from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import time
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
    POST /api/create/<song_id>/

    - song_id 기준으로 Song + Word 정보를 조회
    - build_suno_prompt 로 프롬프트 생성 (request_suno_generate 내부)
    - Suno /generate 호출 → taskId 획득
    - taskId 로 /generate/record-info 를 여러 번 폴링해서 SUCCESS 나올 때까지 대기
    - 최종 응답에서 sunoData 배열을 파싱해서
        * DB(SongDetail, History)에 저장
        * 프론트에는 정제된 JSON만 내려줌
    """

    def post(self, request, song_id: int):
        # 1) Song 조회
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response(
                {"detail": "해당 song_id의 곡을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2) Song 에 연결된 Word 들
        words_qs = song.words.all()

        # 3) 요청 바디에 옵션이 있으면 Suno 옵션으로 사용
        extra_options = request.data if isinstance(request.data, dict) else None

        # 4) Suno /generate 호출 (프롬프트 생성 + generate)
        try:
            generate_result = request_suno_generate(song, words_qs, extra_options)
        except Exception as e:
            return Response(
                {
                    "detail": "Suno /generate 호출 중 오류가 발생했습니다.",
                    "error": str(e),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # generate_result 예시: {"code":200,"msg":"success","data":{"taskId":"..."}}
        task_id = None
        if isinstance(generate_result, dict):
            task_id = (generate_result.get("data") or {}).get("taskId")

        if not task_id:
            # taskId 자체를 못 받았으면 그대로 응답
            return Response(generate_result, status=status.HTTP_502_BAD_GATEWAY)

        # 5) taskId 로 /generate/record-info 폴링 (PENDING → SUCCESS 기다린다)
        final_result = None
        max_attempts = 5   # 최대 5번
        delay_seconds = 3  # 3초 간격

        for attempt in range(max_attempts):
            try:
                status_result = request_suno_task_status(task_id)
                final_result = status_result

                data_block = final_result.get("data") or {}
                status_str = data_block.get("status")

                # 성공하면 루프 종료
                if status_str == "SUCCESS":
                    break

                # 에러 상태면 바로 종료하고 그 상태 그대로 돌려보냄
                if status_str in ("FAILED", "ERROR", "SENSITIVE_WORD_ERROR"):
                    break

            except Exception:
                # 상태 조회에 실패하면 generate_result라도 돌려줄 수 있게 break
                final_result = generate_result
                break

            time.sleep(delay_seconds)

        if final_result is None:
            final_result = generate_result

        # 6) 최종 응답에서 sunoData 파싱 + DB 저장 + 프론트용 형태로 가공
        data_block = final_result.get("data") or {}
        status_str = data_block.get("status")
        task_id_final = data_block.get("taskId") or task_id
        response_block = data_block.get("response") or {}

        # 실제 Suno 응답: response.sunoData 배열
        tracks = response_block.get("sunoData") or []
        # 혹시 다른 형태(response.data)일 수도 있으니 방어
        if not tracks:
            tracks = response_block.get("data") or []

        # ----- DB 저장 (SUCCESS 이고 트랙이 있을 때만) -----
        if status_str == "SUCCESS" and tracks:
            first = tracks[0]

            audio_url = (
                first.get("audioUrl")
                or first.get("audio_url")
                or first.get("sourceAudioUrl")
                or ""
            )
            duration = first.get("duration", 0)
            lyrics = first.get("prompt", "") or first.get("lyrics", "") or ""

            SongDetail.objects.create(
                song=song,
                song_url=audio_url,
                runtime=int(duration) if isinstance(duration, (int, float)) else 0,
                lyrics=lyrics,
            )
            History.objects.get_or_create(song=song, defaults={"count": 0})

        # ----- 프론트로 내려줄 데이터만 추려서 만들기 -----
        tracks_for_client = []
        for t in tracks:
            audio_url_for_client = (
                t.get("audioUrl")
                or t.get("audio_url")
                or t.get("sourceAudioUrl")
                or ""
            )
            tracks_for_client.append(
                {
                    "id": t.get("id"),
                    "audio_url": audio_url_for_client,
                    "title": t.get("title", ""),
                    "tags": t.get("tags", ""),
                    "duration": t.get("duration", 0),
                }
            )

        # 최종적으로 프론트에 내려갈 JSON
        response_body = {
            "code": final_result.get("code", 200),
            "msg": final_result.get("msg", "success"),
            "data": {
                "taskId": task_id_final,
                "status": status_str,
                "response": {
                    "data": tracks_for_client,
                },
            },
        }

        return Response(response_body, status=status.HTTP_201_CREATED)