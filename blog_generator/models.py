from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    link = models.URLField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
