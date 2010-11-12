from django.db import models
from django.contrib.auth.models import *

class Game(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    creator = models.ForeignKey(User)
    
        

class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    joined = models.DateTimeField(auto_now_add=True)


    def currentGame(self):
        self.game_set.all[0]
	
	def name(self):
		return "self.user.name"

    
class Fact(models.Model):
    player = models.ForeignKey(Player)
    
    class Meta:
        abstract = True
    
#Specific to "Role" game
class Role(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class PlayerRole(models.Model):
    player = models.OneToOneField(Player)
    role = models.ForeignKey(Role)
    
    
    def __str__(self):
        return str(self.player.user) + " as " + str(self.role)
    

#Specific to "Role" game
class RoleFact(Fact):
    role = models.ForeignKey(Role)  
    neg = models.BooleanField()
    
    def __str__(self):
        if self.neg:
            return str(self.player.user) + " is not the " + str(self.role)
        else:
            return str(self.player.user) + " is the " + str(self.role)
    
#Nonspefic, could be used to deliver any sort of Fact to a player
class Clue(models.Model):
    player = models.ForeignKey(Player)
    #this will change when we have more kinds of facts
    fact = models.ForeignKey(RoleFact)
    game = models.ForeignKey(Game)
    sent = models.BooleanField()
    send_time = models.DateTimeField()
    
    def __str__(self):
        return "For %s : %s" % (self.player.user, str(self.fact))