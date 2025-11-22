from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------------------------------------------
# Song
# ---------------------------------------------------------
class Song(models.Model):
    title = models.CharField(max_length=100)
    language = models.CharField(max_length=20)
    genre = models.CharField(max_length=30)
    mood = models.CharField(max_length=30)
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


# ---------------------------------------------------------
# Playlist
# ---------------------------------------------------------
class Playlist(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="playlist_items"
    )
    user = models.ForeignKey(
        User,
        to_field="username",
        db_column="username",
        on_delete=models.CASCADE,
        related_name="playlist_items",
        null=True,  # 추가
        blank=True,  # 추가
    )
    is_creator = models.BooleanField(default=False)

    class Meta:
        unique_together = ("song", "user")

    def __str__(self):
        return f"{self.user.username} - {self.song.title}"


# ---------------------------------------------------------
# SongDetail
# ---------------------------------------------------------
class SongDetail(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="details"
    )
    song_url = models.URLField()
    runtime = models.PositiveIntegerField()
    lyrics = models.TextField()

    def __str__(self):
        return f"Detail for {self.song.title}"

# ---------------------------------------------------------
# Word
# ---------------------------------------------------------
class Word(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="words"
    )
    word = models.CharField(max_length=100)
    meaning = models.TextField()

    def __str__(self):
        return f"{self.word} ({self.song.title})"


# ---------------------------------------------------------
# History
# ---------------------------------------------------------
class History(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="histories"
    )
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.song.title}: {self.count}"
