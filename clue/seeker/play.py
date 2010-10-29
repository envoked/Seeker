from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render_to_response

NUM_PLAYERS = 4

def play(request):
    users = User.objects.all()[:NUM_PLAYERS]
    
    game = Game(
        start = datetime.now(),
        end = datetime.now(),
        creator = users[0]
    )
    game.save()
    
    #we do list() because were going to need to get one item at a time out and we dont want to re-SELECT
    roles = list(Role.objects.order_by('?').all()[:NUM_PLAYERS])
    
    for user in users:
        role = roles[0]
        roles = roles[1:]
        
        player = Player(
            user = user,
            game = game,
            role = role
        )
        player.save()
        
    gameplay = Gameplay(game)
    game = gameplay.clues()

    context = {
        'game': game
    }

    return render_to_response("play.html", context)

class Gameplay():
    
    def __init__(self, game):
        self.game = game
        self.num_players = game.player_set.count()
            
    def _create_player_roles(self):
        """
        Gives each player a playerRole
        """
        players = self.game.player_set.all()
        for player in players:
            player_roles_used = []
            for i in range(0, self.num_players):
                is_not_role = Role.objects.exclude(id=player.role.id).exclude(id__in=player_roles_used)[0]
                pr = PlayerRole(
                    player = player,
                    role = is_not_role,
                    neg = True
                )
                player_roles_used.append(is_not_role.id)
                pr.save()
        
    def clues(self):
        """
        Gives a clue to each player
        -will not give a clue to a player about that player
        -will not give a clue based on a PlayerRole fact already used
        """
        self._create_player_roles()

        
        #PlayerRoles already given away
        prs_given = []
        players = self.game.player_set.all()
        
        for i in range(0, self.num_players):
            for player in players:
                #select a PlayerRole that does not describe the player getting the clue
                try:
                    pr = PlayerRole.objects.exclude(player=player).exclude(id__in=prs_given).order_by('?')[0]
                except:
                    print "error finding fact for " + str(player)
                    print "unused facts", PlayerRole.objects.exclude(id__in=prs_given).all()
                    print PlayerRole.objects.all()
                    break
                    
                clue = Clue(
                    player = player,
                    subject_role = pr,
                    game = self.game
                )
                clue.save()
                prs_given.append(pr.id)
        
        return self.game