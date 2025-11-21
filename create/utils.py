from .models import Song


def translate_word_with_google(word: str, source: str = "auto", target: str = "ko"):
    """
    TODO: 실제 Google Translate API 연동 필요.
    현재는 테스트용 더미값 반환.
    """
    return [
        f"{word} 번역1",
        f"{word} 번역2",
        f"{word} 번역3",
    ]


class SunoClient:
    """
    TODO: 실제 Suno AI 연동하기.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def generate_song(
        self,
        song: Song,
        duration_sec: int = 60,
        model: str = "suno_v3_5",
        extra_prompt: str | None = None,
    ):
        """
        TODO: Suno 호출 후 결과 반환.
        지금은 더미 값.
        """
        dummy_url = f"https://example.com/audio/{song.pk}.mp3"
        dummy_lyrics = f"Dummy lyrics for {song.title}"
        dummy_keywords = ["study", "focus", "memory"]

        return {
            "song_url": dummy_url,
            "runtime": duration_sec,
            "lyrics": dummy_lyrics,
            "keywords": dummy_keywords,
        }
