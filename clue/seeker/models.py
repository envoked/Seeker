import traceback
from django.db import models
from django.db import IntegrityError
from django.contrib.auth.models import *
from django.core.exceptions import MultipleObjectsReturned

class Game(models.Model):
    start = models.DateTimeField()
    is_current = models.BooleanField(default=True)
    board_size = models.IntegerField()
            
    def __str__(self):
        return " current: %s" % (self.is_current)
        
    def get_players_within(self, x, y, distance):
        """
        Get players within distance space of x, y
        Diagnals allowed
        """
        players =  self.player_set.filter(
            x__gte = x-distance,
            x__lte = x+distance,
            y__gte = y-distance,
            y__lte = y+distance,
            ).exclude(pk=self.id)
        return players
    
    def other_players(self, player):
        return self.player_set.exclude(id=player.pk)

class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    is_current = models.BooleanField(default=True)
    joined = models.DateTimeField(auto_now_add=True)
    x = models.IntegerField(null=True,)
    y = models.IntegerField(null=True)
    
    def current_game(self):
        self.game_set.all[0]

    def get_position(self):
        if self.x and self.y:
            return (self.x, self.y)
        else:
            return None

    def set_random_position(self):
        import random
        searching = True
        
        players = self.game.player_set.all()
        tries = 100
        tried = list()
        
        for i in range(0, tries):
            x = random.randint(0, self.game.board_size-1)
            y = random.randint(0, self.game.board_size-1)
            tried.append((x, y))
            #print "trying %s" % str((x, y))
            if (x, y) in tried:
                #print "%s in tried" % str((x, y))
                #continue
                pass
            
            taken = False
            for player in players:
                if x == player.x and y == player.y:
                    taken = True
                    
            if taken: continue        
            
            #print "Saving player %s at unoccupied %s" % (str(self), str((x, y)))
            self.x = x
            self.y = y
            self.save()
            return True

        return False
    
    def move_to(self, x, y):
        space_occupied = self.game.player_set.filter(x=x, y=y).all()
        if len(space_occupied) > 0: raise ValueError("Player %s is already here" % space_occupied)
        
        self.x = x
        self.y = y
        self.save()
        return True
                
    def move(self, direction):
        x = self.x
        y = self.y
        if direction == 'left':
            x-=1
        elif direction == 'right':
            x+=1
        elif direction == 'up':
            y-=1
        elif direction == 'down':
            y+=1
        else:
            raise ValueError("Invalid Direction")

        if x<0 or x > self.game.board_size-1 or y<0 or y>self.game.board_size-1:
            raise ValueError("Invalid Direction")
        
        space_occupied = self.game.player_set.filter(x=x, y=y).all()
        if len(space_occupied) > 0: raise ValueError("Player %s is already here" % space_occupied)
          
        self.x = x
        self.y = y
        self.save()
        return True

    def investigate(self, player):
        """
        Move a ClueOwnership from player to self and return it.
        If player has nothing that self doesn't already know, return False"""
        to_learn = player.clueownership_set.order_by('?')[0]
        co = ClueOwnership(
            clue = to_learn.clue,
            player = self,
            source = to_learn
        )
        try:
            self.clueownership_set.add(co)
            self.save()
            return co
        except IntegrityError:
            return False
        
    def explain_clues(self):
        o = ""
        for clue in self.clueownership_set.select_related('clue').order_by('clue__fact__neg').all():
            o += str(clue) + "\n"
        return o
    
    def can_guess_without_deduction(self):
        """
        Does this player have a positive fact about every other player?
        """
        others = self.game.player_set.exclude(pk=self.id).all()
        
        not_found = 0
        for other in others:
            co = self.clueownership_set.select_related('clue').filter(clue__fact__neg=False, clue__fact__player = other).all()
            #print "seeing if %s knows about %s" % (self.playerrole, other.playerrole)
            if len(co) == 0: not_found += 1
                
        #print "There are %d facts that %s does not positively know" % (not_found, self.playerrole)
        if not_found <= 1: return True
        else: return False

    def __str__(self):
        if not self.is_current:
            return '%s (not current) in %s' % (self.user.username, str(self.game))
        else:
            return '%s (current) in %s at %s' % (self.user.username, str(self.game), str(self.get_position()))
    
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
        return str(self.role)
    
#Specific to "Role" game
class RoleFact(Fact):
    role = models.ForeignKey(Role)  
    neg = models.BooleanField()
    
    def __str__(self):
        if self.neg:
            return "The " + str(self.role) + " is not " + str(self.player.user.username)
        else:
            return "The " + str(self.role) + " is " + str(self.player.user.username)
    
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
    player = models.OneToOneField(Player)
    game = models.ForeignKey(Game)
    created = models.DateTimeField(auto_now_add=True)
    
    def human_rank(self):
        suffixes = {1:'st', 2:'nd', 3:'rd'}
        if self.rank+1 in suffixes:
            return str(self.rank+1) + suffixes[self.rank+1]
        else:
            return str(self.rank+1) + 'th'
    
#Nonspefic, could be used to deliver any sort of Fact to a player
class Clue(models.Model):
    #this will change when we have more kinds of facts
    fact = models.ForeignKey(RoleFact)
    game = models.ForeignKey(Game)
    sent = models.BooleanField(default=False)
    send_time = models.DateTimeField(null=True)
    
    def __str__(self):
        return "%s" % str(self.fact)
        
class ClueOwnership(models.Model):
    clue = models.ForeignKey(Clue)
    player = models.ForeignKey(Player)
    source = models.ForeignKey('ClueOwnership', null=True, related_name='child_clues')
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.source:
            return "%s told %s that that %s" % (self.source.player.user.username, self.player.user.username, str(self.clue))
        else:
            return "%s knows that %s" % (self.player.user.username, str(self.clue))
        
    class Meta:
        # One clue can be owned by multiple players, but not by the same player
        unique_together = ('player', 'clue')
        
class Turn(models.Model):
    action = models.CharField(max_length=100)
    params = models.CharField(max_length=100)
    player = models.ForeignKey(Player)
    created = models.DateTimeField(auto_now_add=True)