from models import *

class BasicRoleGame():
    
    def __init__(self, game):
        self.game = game
        self.num_clues = 4
        self.num_players = game.player_set.count()
        self.process_players()
            
    def process_players(self):
        """
        Gives each player a playerRole
        """
        #we do list() because were going to need to get one item at a time out and we dont want to re-SELECT
        roles = list(Role.objects.order_by('?').all()[:self.num_players])
    
        players = self.game.player_set.all()
        for player in players:
            role = roles[0]
            roles = roles[1:]
            player_roles_used = []
 
            pr = PlayerRole(
                player = player,
                role = role
            )
            
            for i in range(0, self.num_clues):
 
                pr.save()
                is_not_role = Role.objects.exclude(id=player.playerrole.id).exclude(id__in=player_roles_used)[0]
                pr = RoleFact(
                    player = player,
                    role = is_not_role,
                    neg = True
                )
                player_roles_used.append(is_not_role.id)
                pr.save()
        
    def play(self):
        """
        Gives a clue to each player
        -will not give a clue to a player about that player
        -will not give a clue based on a PlayerRole fact already used
        """

        #PlayerRoles already given away
        prs_given = []
        players = self.game.player_set.all()
        
        for i in range(0, self.num_clues):
            for player in players:
                #select a PlayerRole that does not describe the player getting the clue
                try:
                    pr = RoleFact.objects.exclude(player=player).exclude(id__in=prs_given).order_by('?')[0]
                except:
                    print "error finding fact for " + str(player)
                    print "unused facts", PlayerRole.objects.exclude(id__in=prs_given).all()
                    print RoleFact.objects.all()
                    break
                    
                clue = Clue(
                    player = player,
                    fact = pr,
                    game = self.game
                )
                clue.save()
                prs_given.append(pr.id)
        
        return self.game