from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Song(models.Model):
    # Song : Song_ID, create_user, title, language, genre, mood
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=20)
    genre = models.CharField(max_length=50)
    mood = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title} ({self.create_user})"


class Playlist(models.Model):
    # Playlist : Song_ID, username, song_title
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song_title = models.CharField(max_length=200)

    class Meta:
        unique_together = ("song", "user")

    def __str__(self):
        return f"{self.user} - {self.song_title}"


class SongDetail(models.Model):
    # Song_Detail : Song_ID, create_user, song_url, runtime, lylics, keywords
    song = models.OneToOneField(Song, on_delete=models.CASCADE)
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    song_url = models.URLField()
    runtime = models.IntegerField()
    lyrics = models.TextField()
    # JSON 형태로 저장
    keywords = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Detail of {self.song_id}"


class Word(models.Model):
    # Word : Song_ID, create_user, word
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="words")
    create_user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.word} ({self.song_id})"


class History(models.Model):
    # History : Song_ID, Count
    song = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="history")
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"History {self.song_id}: {self.count}"
