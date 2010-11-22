from models import *
from distributor import *
from datetime import datetime, timedelta


class BasicRoleGame():
    
    def __init__(self, game):
        self.game = game
        self.num_players = game.player_set.count()
        self.num_clues = self.num_players - 1 # Number of clues per player
            
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
            pr.save()
            
            # Create clues
            for i in range(0, self.num_clues):    
                is_not_role = Role.objects.exclude(id=player.playerrole.id).exclude(id__in=player_roles_used)[0]
                rf = RoleFact(
                    player = player,
                    role = is_not_role,
                    neg = True
                )
                player_roles_used.append(is_not_role.id)
                rf.save()
        
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
            
            if i == 0:
                time_to_send = now
            else:
                duration = self.game.end - self.game.start
                interval_to_send = (duration.seconds / 60) / self.num_clues
                time_to_send = self.game.start + timedelta(minutes=(interval_to_send * i))

            for player in players:
                #select a PlayerRole that does not describe the player getting the clue
                try:
                    pr = RoleFact.objects.exclude(player=player).exclude(id__in=prs_given).order_by('?')[0]
                except:
                    #print "error finding fact for " + str(player)
                    #print "unused facts", PlayerRole.objects.exclude(id__in=prs_given).all()
                    #print RoleFact.objects.all()
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
                
        return self.game
    
    def check_submission(self, submission):
        number_correct = 0

        for guess in submission.roleguess_set.all():
            pr = PlayerRole.objects.get(player = guess.other_player)            
            if pr.role != guess.role:
                guess.correct = False
            else:
                guess.correct = True
                number_correct+=1
                
            guess.save()
        
        submission.checked = True
        submission.score = number_correct
        submission.save()
        
        
    def create_rankings(self):
        rank = 0
        submissions = self.game.submission_set.order_by('-score').all()
        for submission in submissions:
            ranking = Ranking(
                rank = rank,
                submission = submission,
                player = submission.player,
                game = self.game
            )
            ranking.save()
            rank+=1
            
        self.game.is_current = False
        self.game.save()
        