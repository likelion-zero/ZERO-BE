# create/api.py


import os
from typing import Iterable, Dict, Any

import requests
from django.conf import settings

from create.utils.gemini import get_meanings
from .models import Song, Word



def get_word_meanings(word: str):
    return get_meanings(word, top_k=3)




# ============================
# Suno API 연동 유틸 함수들
# ============================

SUNO_BASE_URL = "https://api.sunoapi.org/api/v1"


def _get_suno_api_key() -> str:
    """
    Suno API Key 를 환경변수 또는 settings 에서 가져온다.
    """
    api_key = os.environ.get("SUNO_API_KEY") or getattr(settings, "SUNO_API_KEY", None)
    if not api_key:
        raise RuntimeError(
            "Suno API Key 가 설정되지 않았습니다. "
            "환경변수 SUNO_API_KEY 또는 settings.SUNO_API_KEY 를 확인하세요."
        )
    return api_key




# ★ 새로 추가: callback URL 가져오는 함수
def _get_suno_callback_url() -> str:
    """
    Suno 콜백 URL 을 환경변수 또는 settings 에서 가져온다.
    없으면 기본값을 사용한다.
    """
    callback_url = (
        os.environ.get("SUNO_CALLBACK_URL")
        or getattr(settings, "SUNO_CALLBACK_URL", None)
    )
    if not callback_url:
        # 로컬 테스트용 기본값 (원하면 나중에 꼭 바꾸기)
        callback_url = "https://example.com/suno/callback"
    return callback_url






def build_suno_prompt(song: Song, words: Iterable[Word]) -> str:
    """
    Song + Word 정보로 Suno에 넘겨줄 프롬프트를 생성한다.
    """
    vocab_parts = [f"{w.word} ({w.meaning})" for w in words]
    vocab_str = ", ".join(vocab_parts) if vocab_parts else ""

    prompt = (
        f"Create a {song.genre} song in {song.language} for language learning.\n"
        f"Mood: {song.mood}.\n"
        f"Song title: {song.title}.\n"
    )

    if vocab_str:
        prompt += f"Include and emphasize these vocabulary words: {vocab_str}.\n"

    return prompt


def request_suno_generate(
    song: Song,
    words: Iterable[Word],
    options: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Suno 'generate' 엔드포인트 호출.
    - song, words 로 prompt 생성
    - options 로 model, instrumental 등 추가 옵션을 덮어쓸 수 있음
    """
    api_key = _get_suno_api_key()
    prompt = build_suno_prompt(song, words)
    callback_url = _get_suno_callback_url() # 추가

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "customMode": False,
        "instrumental": False,
        "model": "V3_5",
        "callBackUrl": callback_url,  # 기본 콜백 URL 세팅
    }

    if options:
        # Suno 문서 기준으로 허용할만한 key 들만 반영
        allowed_keys = {
            "customMode",
            "instrumental",
            "model",
            "callBackUrl",
            "style",
            "title",
        }
        for key, value in options.items():
            if key in allowed_keys:
                payload[key] = value

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        f"{SUNO_BASE_URL}/generate",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def request_suno_task_status(task_id: str) -> Dict[str, Any]:
    """
    Suno 'generate/record-info' 엔드포인트로 task 상태 조회.
    """
    api_key = _get_suno_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    resp = requests.get(
        f"{SUNO_BASE_URL}/generate/record-info",
        headers=headers,
        params={"taskId": task_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
