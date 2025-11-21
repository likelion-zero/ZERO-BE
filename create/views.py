from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SongCreateSerializer


class SongCreateView(APIView):
    def post(self, request):
        serializer = SongCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        song = serializer.save()

        # 프론트로 보내줄 응답
        return Response(
            {
                "success": True,
                "message": "곡과 단어가 DB에 저장되었습니다. 이제 Suno AI 리퀘스트를 보내세요.",
                "next_action": "CALL_SUNO",
                "song": {
                    "id": song.id,
                    "title": song.title,
                    "language": song.language,
                    "genre": song.genre,
                    "mood": song.mood,
                    "created_by": song.user.username,
                },
            },
            status=status.HTTP_201_CREATED,
        )