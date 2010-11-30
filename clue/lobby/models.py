from django.db import models
from django.contrib.auth.models import *
from seeker.models import Game

class Lobby(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User)
    num_players = models.IntegerField()
    hours = models.IntegerField()
    minutes = models.IntegerField()
    #created = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    
    #Once a lobby turns into a game, this will reference it ant the lobby is dead
    game = models.ForeignKey(Game, null=True)
    
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
    created = models.DateTimeField(auto_now_add=True)
    lobby = models.ForeignKey(Lobby, related_name='messages')