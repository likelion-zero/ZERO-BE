import os
import json
import requests

SUNO_BASE_URL = "https://api.sunoapi.org/api/v1"





def main():
    # 👉 여기 prompt / 옵션을 네가 마음대로 바꿔서 테스트하면 됨
    prompt = (
        "Create a K-pop style song in Japanese for language learning.\n"
        "Mood: happy and energetic.\n"
        "Song title: Wordly Vocabulary Song.\n"
        "Include and emphasize these vocabulary words: 学校(school), 音楽(music), 友達(friend).\n"
    )

    payload = {
        "prompt": prompt,
        "model": "V3_5",
        "customMode": False,
        "instrumental": False,
        # 필요하면 콜백 URL도 넣을 수 있음 (선택)
        "callBackUrl": "https://example.com/suno/callback",
        # "style": "kpop, upbeat",
        # "title": "My Test Song",
    }

    api_key = '9d427129172c5425fbf43412acd18f60'

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print("=== Suno /generate 요청 보내는 중 ===")
    print("요청 payload:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    resp = requests.post(
        f"{SUNO_BASE_URL}/generate",
        headers=headers,
        json=payload,
        timeout=30,
    )

    print("\n=== 응답 status code ===")
    print(resp.status_code)

    try:
        data = resp.json()
        print("\n=== 응답 JSON ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except ValueError:
        print("\n=== 응답 원문(text) ===")
        print(resp.text)

def get_suno_task_details(task_id: str):
    api_key = '9d427129172c5425fbf43412acd18f60'
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    params = {
        "taskId": task_id
    }
    response = requests.get(
        f"{SUNO_BASE_URL}/generate/record-info",
        headers=headers,
        params=params,
        timeout=30,
    )

    print("=== 응답 status code ===")
    print(response.status_code)

    try:
        data = response.json()
        print("=== 응답 JSON ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except ValueError:
        print("=== 응답 텍스트 ===")
        print(response.text)

    return response

if __name__ == "__main__":
    get_suno_task_details("ab2043f1e8dcaa5c9a28f360877d0e2a")
