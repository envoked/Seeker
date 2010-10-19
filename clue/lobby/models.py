from django.db import models
from django.contrib.auth.models import *

class Lobby(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    
class Member(models.Model):
    lobby = models.ForeignKey(Lobby, related_name='members')
    user = models.ForeignKey(User, related_name='lobbies')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('lobby', 'user')
    
class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(User, related_name='sent')
    to = models.ForeignKey(User, related_name='received')
