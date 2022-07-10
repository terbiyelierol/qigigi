from unicodedata import category
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Listing(models.Model):
  user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
  title = models.CharField(max_length=150)
  date_posted = models.DateField(auto_now_add=True)
  price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
  category = models.CharField(max_length=30,default="other")
  description = models.TextField(max_length=500)
  picture = models.URLField(max_length=200)
  location = models.CharField(max_length=7)
  geolocation = models.CharField(max_length=100, default='{"lat": 43.654,"lng": -79.3883 }')

