from django.db import models
from django.contrib.auth.models import *
from django.conf import settings

import os, glob

class Lobby(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User)
    #num_players = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    creator_image = models.ImageField(upload_to="/img/chars", blank="char1.png")
    
    #Once a lobby turns into a game, this will reference it ant the lobby is dead
    game = models.ForeignKey('seeker.Game', null=True)

    @staticmethod
    def default_cpu_image():
        return 'img/chars/char1.png'

    @staticmethod
    def getCharImages():
        images = []
        path = '%simg/chars' % settings.MEDIA_ROOT
        print path
        #for infile in glob.glob( os.path.join(path) ):
        for infile in os.listdir(path):
            if(infile.find(".png") != -1):
                images.append(infile)

        return images

    
class Member(models.Model):
    lobby = models.ForeignKey(Lobby, related_name='members')
    user = models.ForeignKey(User, related_name='lobbies')
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="/img/chars", blank="char1.png")
    
    class Meta:
        unique_together = ('lobby', 'user')

    def set_player_image(self, char):
        this.image = char
        this.save()

class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(User, related_name='sent')
    to = models.ForeignKey(User, related_name='received')
    created = models.DateTimeField(auto_now_add=True)
    lobby = models.ForeignKey(Lobby, related_name='messages')
