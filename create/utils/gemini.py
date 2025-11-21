import google.generativeai as genai
from django.conf import settings
from typing import List
import os

# 클라이언트 객체 대신 API 키를 설정하는 함수
def init_gemini():

    api_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_KEY
    if not api_key:
        # 이전에 설정된 예외 처리 유지
        raise RuntimeError("GEMINI_KEY가 Django settings에 설정되지 않았습니다. 또는 환경 변수를 확인하세요.")

    genai.configure(api_key=api_key)


def get_meanings(word: str, top_k: int = 3) -> List[str]:
    """
    단어 1개를 넣으면 Gemini를 사용해 한국어 의미 상위 top_k개를 리스트로 반환합니다.
    """
    init_gemini()

    model = genai.GenerativeModel("gemini-2.5-flash") 

    prompt = f"""
    단어 "{word}"의 한국어 의미를 의미 관련도가 높은 순서대로 {top_k}개만 출력해.
    - 번호, 기호 없이
    - 각 줄마다 하나의 의미만
    - 예문, 추가 설명, 영어 번역 금지
    - 출력은 오직 {top_k}개의 의미만 포함해야 해.
    """

    # generate_content 호출
    res = model.generate_content(prompt)
    text = (res.text or "").strip()

    # 결과 정리 로직 유지
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines[:top_k]