from django.db import models
from datetime import datetime

# Create your models here.
class VideoUrl(models.Model):
	url=models.CharField(max_length=128)
	videoname=models.CharField(max_length=128)
	uploaded_time=models.DateTimeField()
	def save(self):
		self.uploaded_time=datetime.now()
		models.Model.save(self)

class VideoRating(models.Model):
	RATINGS=(
	(0,0),
	(1,1),
	(2,2),
	(3,3),
	(4,4),
	(5,5),
	)
	video=models.ForeignKey(VideoUrl)
	rating=models.IntegerField(default=5,choices=RATINGS)
