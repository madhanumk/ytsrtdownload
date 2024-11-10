from django.db import models

# Create your models here.


class Youtube_Video(models.Model):
    video_id = models.CharField(max_length=20)
    video_name = models.CharField(max_length=250)
    srt = models.FileField(upload_to="srt")
    data = models.JSONField()

    def __str__(self):
        return self.video_name

