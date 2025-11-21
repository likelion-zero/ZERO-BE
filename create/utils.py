from .models import Song


def translate_word_with_google(word: str, source: str = "auto", target: str = "ko"):
    """
    TODO: 실제 Google Translate API 연동
    지금은 더미 구현으로, 프론트 개발용 구조만 맞춰줌.
    """
    # 실제 구현 시: word -> 여러 번역 후보 리스트 반환
    return [
        f"{word} 번역1",
        f"{word} 번역2",
        f"{word} 번역3",
    ]


class SunoClient:
    """
    TODO: 실제 Suno AI 연동
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def generate_song(self, song: Song, duration_sec: int = 60,
                      model: str = "suno_v3_5", extra_prompt: str | None = None):
        """
        실제로는 Suno API 호출해서 mp3 url, 가사, runtime 등을 받아와야 함.
        지금은 더미 데이터 반환.
        """

        dummy_audio_url = f"https://example.com/audio/{song.pk}.mp3"
        dummy_lyrics = f"Dummy lyrics for {song.title}"
        dummy_keywords = "keyword1,keyword2,keyword3"

        return {
            "runtime": duration_sec,
            "audio_url": dummy_audio_url,
            "lyrics": dummy_lyrics,
            "keywords": dummy_keywords,
        }
