from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SongCreateSerializer
from create.api import get_word_meanings


class CreateSongView(APIView):
    def post(self, request):
        serializer = SongCreateSerializer(data=request.data)

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