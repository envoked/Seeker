from django.test import TestCase
from seeker.models import *
from django.contrib.auth.models import *
from datetime import *

class GameTest(TestCase):
    fixtures = ['auth.json', 'seeker.json']
    num_players = 4
    
    def _create_game_and_players(self):
        """
        Creates a game and players
        """
        users = User.objects.all()
        
        game = Game(
            start = datetime.now(),
            end = datetime.now(),
            creator = users[0]
        )
        game.save()
        
        #we do list() because were going to need to get one item at a time out and we dont want to re-SELECT
        roles = list(Role.objects.order_by('?').all()[:self.num_players])
        
        for user in users[0:self.num_players]:
            role = roles[0]
            roles = roles[1:]
            
            player = Player(
                user = user,
                game = game,
                role = role
            )
            player.save()
            
    def _create_player_roles(self):
        """
        Gives each player a playerRole
        """
        players = Player.objects.all()
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
        
    def test_one_round(self):
        """
        Gives a clue to each player
        -will not give a clue to a player about that player
        -will not give a clue based on a PlayerRole fact already used
        """
        self._create_game_and_players()
        self._create_player_roles()
        
        players = Player.objects.all()
        print "\nPlayers:"
        print players
        
        print PlayerRole.objects.all().count()
        
        #PlayerRoles already given away
        prs_given = []
        
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
                    subject_role = pr
                )
                clue.save()
                prs_given.append(pr.id)
        
        clues = Clue.objects.all()
        
        print "\nClues:"
        for clue in clues:
            print clue
        
            
