from django.db import models

# Create your models here.

class SocialHandle(models.Model):
  name = models.CharField(max_length=25)
  url = models.CharField(max_length=500)
  icon_class = models.CharField(max_length=25)
  
  def __str__(self):
    return self.name