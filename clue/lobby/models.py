from django.db import models
from django.contrib.auth.models import *
from seeker.models import Game
from files import get_profile_path

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
    
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='profile_thumb', blank=True, null=True,
          editable=False)
    
    def save(self, force_insert=False, force_update=False):
        #get mtime stats from file
        thumb_update = False
        print self

        if self.thumbnail:
            statinfo1 = os.stat(self.photo.path)
            statinfo2 = os.stat(self.thumbnail.path)
            if statinfo1 > statinfo2:
                thumb_update = True

        if self.photo and not self.thumbnail or thumb_update:
            from PIL import Image

            THUMB_SIZE = (150, 150)

            #self.thumbnail = self.photo

            image = Image.open(self.photo.path)

            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
            (head, tail) = os.path.split(self.photo.path)
            (a, b) = os.path.split(self.photo.name)

            if not os.path.isdir(head + '/thumbs'):
                os.mkdir(head + '/thumbs')

            image.save(head + '\\thumbs\\' + tail)

            self.thumbnail = a + '/thumbs/' + b

        super(UserProfile, self).save()

    
class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(User, related_name='sent')
    to = models.ForeignKey(User, related_name='received')
    created = models.DateTimeField(auto_now_add=True)
    lobby = models.ForeignKey(Lobby, related_name='messages')