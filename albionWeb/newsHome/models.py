from django.db import models

# Create your models here.
class NewsItem(models.Model):
    newsTitle = models.CharField(max_length=100)

    link = models.CharField(max_length=120)
    image = models.CharField(max_length=120)
    blurb = models.TextField()
    website = models.CharField(max_length=50)
    captured_date = models.DateField()

