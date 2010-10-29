from django.db import models
from django.contrib.auth.models import *

class Game(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    creator = models.ForeignKey(User)

class Role(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class Player(models.Model):
    user = models.ForeignKey(User)
    role = models.ForeignKey(Role)
    game = models.ForeignKey(Game)
    joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user) + " as " + str(self.role)
    
class PlayerRole(models.Model):
    player = models.ForeignKey(Player)
    role = models.ForeignKey(Role)  
    neg = models.BooleanField()
    
    def __str__(self):
        if self.neg:
            return str(self.player.user) + " is not the " + str(self.role)
        else:
            return str(self.player.user) + " is the " + str(self.role)
    
class Clue(models.Model):
    player = models.ForeignKey(Player)
    subject_role = models.ForeignKey(PlayerRole)
    game = models.ForeignKey(Game)
    
    def __str__(self):
        return "For %s : %s" % (self.player.user, str(self.subject_role))