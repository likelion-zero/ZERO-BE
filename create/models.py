from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Song(models.Model):
    # AutoField 기본 pk = id 사용해도 되고, 명시하고 싶으면 primary_key=True
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=20)
    genre = models.CharField(max_length=50)
    mood = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.create_user})"


class SongDetail(models.Model):
    song = models.OneToOneField(
        Song, on_delete=models.CASCADE, related_name="detail"
    )
    runtime = models.IntegerField()          # 초 단위
    audio_url = models.URLField()
    lyrics = models.TextField()
    keywords = models.TextField(blank=True)  # 필요하면 JSONField로 교체

    def __str__(self):
        return f"Detail of {self.song_id}"


class Word(models.Model):
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name="words"
    )
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.word} ({self.song_id})"


class History(models.Model):
    song = models.OneToOneField(
        Song, on_delete=models.CASCADE, related_name="history"
    )
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"History {self.song_id}: {self.count}"


class Playlist(models.Model):
    # create 앱에서 관리, playlist 앱은 이걸 import 해서 사용
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="playlist"
    )
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name="in_playlists"
    )
    song_title = models.CharField(max_length=200)
    is_from_chart = models.BooleanField(default=False)
    last_played_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_played_at"]
        unique_together = ("user", "song")

    def __str__(self):
        return f"{self.user} - {self.song_title}"

