import traceback
from django.db import models
from django.db import IntegrityError
from django.contrib.auth.models import *
from django.core.exceptions import MultipleObjectsReturned
from lb.util import expand

class Game(models.Model):
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
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
    
    def get_player_cells_within(self, x, y, distance):
        cells =  PlayerCell.objects.filter(player__in=self.player_set.all()).filter(
            x__gte = x-distance,
            x__lte = x+distance,
            y__gte = y-distance,
            y__lte = y+distance,
            )
        return cells
    
    def other_players(self, player):
        return self.player_set.exclude(id=player.pk)

class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    is_current = models.BooleanField(default=True)
    joined = models.DateTimeField(auto_now_add=True)
    x = models.IntegerField(null=True,)
    y = models.IntegerField(null=True)
    image = models.ImageField(upload_to="/img/chars", blank="char1.png")
    
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

    def get_direction_of_movement(self, new_x, new_y):
        direction = ""
        print "--------------"
        x = int(self.x)
        y = int(self.y)
        new_x = int(new_x)
        new_y = int(new_y)

        print "OLD LOCATION %s , %s" % (x, y)
        print "NEW LOCATION %s , %s" % (new_x, new_y)
        
        if(new_x > x):
            direction = "right"
        elif(new_x < x):
            direction = "left"
        elif(new_y > y):
            direction = "down"
        elif(new_y < y):
            direction = "up"
        else:
            raise ValueError("Invalid Direction")

        return direction
    
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
        to_learn = player.clue_set.order_by('?')[0]
        c = Clue(
            fact = to_learn.fact,
            player = self,
            source = to_learn,
            game = self.game
        )
        try:
            c.save()
            return c
        except IntegrityError:
            return False
        
    def investigate_cell(self, cell):
        known_facts = self.clue_set.filter().values('fact__id')
        to_learn = CellFact.objects.filter(cell=cell, game=self.game).exclude(pk__in=known_facts)
        
        if len(to_learn) > 0:
            c = Clue(
                fact = to_learn[0],
                game = self.game,
                player = self
            )
            try:
                c.save()
                return c
            except IntegrityError:
                return None
        else:
            return None
        
    def explain_clues(self):
        o = ""
        for clue in self.clueownership_set.select_related('clue').order_by('clue__fact__neg').all():
            o += str(clue) + "\n"
        return o
    
    def unkown_facts(self):
        """
        How many guesses is the player away from knowing everthing
        """        
        known_facts = self.clue_set.filter(fact__neg=False).values('fact__player')
        correct_guesses = self.guess_set.filter(correct=True).values('other_player')
        players_left = PlayerRole.objects.filter(player__in=self.game.player_set.all()).exclude(player__in=correct_guesses).exclude(player=self)
        
        return len(players_left)

    def __str__(self):
        return self.user.username
        if not self.is_current:
            return '%s (not current) in %s' % (self.user.username, str(self.game))
        else:
            return '%s (current) in %s at %s' % (self.user.username, str(self.game), str(self.get_position()))

class Cell(models.Model):
    x = models.IntegerField(null=True)
    y = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)

class PlayerCell(Cell):
    player = models.OneToOneField(Player)
   
    def set_random_position(self):
        import random
        searching = True
        
        game = self.player.game
        cells = PlayerCell.objects.filter(player__in=game.player_set.all())
        tries = 100
        tried = list()
        
        for i in range(0, tries):
            x = random.randint(0, game.board_size-1)
            y = random.randint(0, game.board_size-1)
            tried.append((x, y))
            if (x, y) in tried:
                pass
            
            taken = False
            for cell in cells:
                if x == cell.x and y == cell.y:
                    taken = True
                    
            if taken: continue        
            
            print "Saving player %s at unoccupied %s" % (str(self), str((x, y)))
            self.x = x
            self.y = y
            self.save()
            return True

        return False
    
    def __str__(self):
        try:
            return '%s at %d, %s' % (self.player, self.x, self.y)
        except:
            return '%s at ?' % str(self.player)
            
   
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
   
class Fact(models.Model):
    player = models.ForeignKey(Player)
    neg = models.BooleanField()
    game = models.ForeignKey(Game)
    
    def __str__(self):
        try:
            return str(self.rolefact)
        except:
            return str(self.cellfact)
    
#Specific to "Role" game
class RoleFact(Fact):
    fact = models.OneToOneField(Fact)
    role = models.ForeignKey(Role)  
    
    def __str__(self):
        if self.neg:
            return "%s is not the %s" % (str(self.player.user.username), str(self.role))
        else:
            return "%s is the %s" % (str(self.player.user.username), str(self.role))
            
#Specific to "Role" game
class CellFact(Fact):
    fact = models.OneToOneField(Fact)
    cell = models.ForeignKey(Cell)  
    
    def __str__(self):
        if self.neg:
            return "%s's cell is not %d, %d" % (str(self.player.user.username), self.cell.x, self.cell.y)
        else:
            return "%s's cell is %d, %d" % (str(self.player.user.username), self.cell.x, self.cell.y)
    
class Submission(models.Model):
    player = models.ForeignKey(Player)
    checked = models.BooleanField(default=False)
    score = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey(Game)
    
class Guess(models.Model):
    player = models.ForeignKey(Player)
    correct = models.NullBooleanField()
    other_player = models.ForeignKey(Player, related_name='other_player_set')
    role = models.ForeignKey(Role)
    cell = models.ForeignKey(Cell)
    points = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    
class Ranking(models.Model):
    rank = models.IntegerField(null=True)
    total_points = models.IntegerField(null=True)
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
    fact = models.ForeignKey(Fact)
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game, null=True) # todo: remove
    source = models.ForeignKey('Clue', null=True, related_name='child_clues')
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.source:
            return "%s told %s that %s" % (self.source.player.user.username, self.player.user.username, str(self.fact))
        else:
            return "%s knows that %s" % (self.player.user.username, str(self.fact))
        
    def serialize(self):
        ex = expand(self)
        ex['str'] = str(self)
        return ex
        
    class Meta:
        # One clue can be owned by multiple players, but not by the same player
        unique_together = ('player', 'fact')
        
class Turn(models.Model):
    action = models.CharField(max_length=100)
    params = models.CharField(max_length=100)
    player = models.ForeignKey(Player)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str___(self):
        return '%s %s' % (action, str(player))