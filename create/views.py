from django.shortcuts import render

from rest_framework import generics, permissions
from .models import Song
from .serializers import SongSerializer


class SongCreateView(generics.CreateAPIView):
    """
    곡 정보 + 단어 리스트를 받아 Song / Word 생성 후
    생성된 song 정보와 단어 리스트를 반환하는 API

    - POST /api/create/
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    # 로그인 붙일 준비가 되어 있으면 IsAuthenticated 사용,
    # 아직이면 AllowAny 로 시작해도 됨.
    # 명세상 "로그인 유저 기준"이라 우선 인증 필수로 둠.
    permission_classes = [permissions.AllowAny]

