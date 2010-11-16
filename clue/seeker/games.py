from models import *
from distributor import *
from datetime import datetime, timedelta


class BasicRoleGame():
    
    def __init__(self, game):
        self.game = game
        self.num_players = game.player_set.count()
        self.num_clues = self.num_players - 1 # Number of clues per player
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
            roles = roles[1]
            player_roles_used = []
 
            pr = PlayerRole(
                player = player,
                role = role
            )
            
            # Create clues
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
        now = datetime.now()
        print self.game.end
        for i in range(0, self.num_clues):
            #print "start"
            #print self.game.start
            #print "end"
            #print self.game.end
            
            if i == 0:
                time_to_send = now
            else:
                #time_to_send =
                #print "start"
                #print self.game.start
                #print "end"
                #print self.game.end
                duration = self.game.end - self.game.start
                #print "duration:"
                #print duration
                #print "num_clues"
                #print self.num_clues
                
                #this needs work
                interval_to_send = (duration.seconds / 60) / self.num_clues
                #print "interval:"
                #print interval_to_send
                time_to_send = self.game.start + timedelta(minutes=(interval_to_send * i))
                #print "FINAL TIME TO SEND"
                #print time_to_send
                
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
                    game = self.game,
                    sent = 0,
                    send_time = time_to_send
                )
                clue.save()
                prs_given.append(pr.id)
                
        distribute_clues(self.game.id)
        
        return self.game