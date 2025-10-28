from django.db import models

# Create your models here.

class SocialHandle(models.Model):
  name = models.CharField(max_length=25)
  url = models.CharField(max_length=500)
  icon_class = models.CharField(max_length=25)
  
  def __str__(self):
    return self.name
    
class Product(models.Model):
  name = models.CharField(max_length=255)
  type = models.CharField(max_length=25)
  description = models.TextField()
  market_url = models.CharField(max_length=500, blank=True)
  image = models.FileField(upload_to='')
  
  def __str__(self):
    return self.name