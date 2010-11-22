from django.db import models
from django.contrib.auth.models import *

class Game(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    creator = models.ForeignKey(User)
    is_current = models.BooleanField(default=True)
            
    def __str__(self):
        return "%s-%s current: %s" % (self.start, self.end, self.is_current)

class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    is_current = models.BooleanField(default=True)
    joined = models.DateTimeField(auto_now_add=True)
    
    def current_game(self):
        self.game_set.all[0]

    def __str__(self):
        return '%s (active: %s) in %s' % (self.user.username, self.is_current, str(self.game))

    
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
    
class Submission(models.Model):
    player = models.ForeignKey(Player)
    checked = models.BooleanField(default=False)
    score = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey(Game)
    
class Guess(models.Model):
    submission = models.ForeignKey(Submission)
    correct = models.NullBooleanField()
    
    class Meta:
        abstract = True
        
class RoleGuess(Guess):
    other_player = models.ForeignKey(Player, related_name='other_player_set')
    role = models.ForeignKey(Role)
    
class Ranking(models.Model):
    rank = models.IntegerField()
    submission = models.ForeignKey(Submission)
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    created = models.DateTimeField(auto_now_add=True)
    
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