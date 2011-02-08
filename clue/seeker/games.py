import traceback, exceptions, random
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Max
from models import *
from distributor import *
from lb.util import get_logger, expand, serialize_qs

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
                
                clue = self.convert_rf_to_clue(pr, player, time_to_send)
                clue.save()
                
                prs_given.append(pr.id)
                
        return self.game
    
    def convert_rf_to_clue(self,rf,player,time_to_send):   
        clue = Clue(
            player = player,
            fact = rf,
            game = self.game,
            sent = 0,
            send_time = time_to_send
        )
        
        return clue
    
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
        
class BoardGame:
    
    def __init__(self, game):
        self.game = game
        
    def play(self):
        #we do list() because were going to need to get one item at a time out and we dont want to re-SELECT
        roles = list(Role.objects.order_by('?').all()[:self.game.player_set.count()])
        for player in self.game.player_set.all():
            player.set_random_position()
            
            pc = PlayerCell(
                player = player
            )
            pc.save()
            pc.set_random_position()
            pc_clue = CellFact(
                cell = pc,
                player = player,
                neg = False,
                game = self.game
            )
            pc_clue.save()
            
            role = roles[0]
            roles = roles[1:]
            player_roles_used = []
 
            pr = PlayerRole(
                player = player,
                role = role
            )
            pr.save()
            
            rf = RoleFact(
                role = role,
                neg = False,
                player = player,
                game = self.game
            )
            rf.save()
            
            clue = Clue(
                fact = rf,
                game = self.game,
                player = player
            )
            clue.save()
            
        for player in self.game.player_set.all():
            other_players = self.game.player_set.exclude(pk=player.id).order_by('?')
            
            #We know that each other player is not our role
            for other in other_players:
                rf = RoleFact(role = player.playerrole.role, neg=True, player=other, game=self.game)
                rf.save()
                clue = Clue(
                    fact = rf,
                    player = player,
                    game = self.game)
                clue.save()
                
            pc_clue = CellFact(
                cell = player.playercell,
                player = other_players[0],
                neg = True,
                game = self.game
            )
            pc_clue.save()
            
        for player in self.game.player_set.all():
            other_players = self.game.player_set.exclude(pk=player.id).all()
            #We know that each other role is not this player
            for other in other_players:
                rf = RoleFact(role = other.playerrole.role, neg=True, player=player, game=self.game)
                rf.save()
                clue = Clue(
                    fact = rf,
                    player = player,
                    game = self.game)
                clue.save()
    
    def guess(self, user, other_user, role):
        this_player = user.player_set.get(is_current=True, game=self.game)
        other_player = other_user.player_set.get(is_current=True, game=self.game)
        
        if other_player.playerrole.role == role:
            rf = RoleFact(player=other_player, neg=False, role=role)
            rf.save()
            new_clue = Clue(
                fact = rf,
                game = self.game,
                player = this_player
            )
            new_clue.save()
        else:
            rf = RoleFact(player=other_player, neg=True, role=role)
            rf.save()
            new_clue  = Clue(
                fact = rf,
                game = self.game,
                player = this_player
            )
            new_clue.save()
        return new_co
        
    def console_display(self):
        o = ""
        rows = []
        
        for y in range(0, self.game.board_size):
            row = []
            for x in range(0, self.game.board_size):
                try:
                    player_here = self.game.player_set.get(x=x, y=y)
                    
                    row.append("[%s]" % str(player_here.playerrole.role.name[0]))
                except ObjectDoesNotExist:
                    row.append("[ ]")
                except:
                    traceback.print_exc()
                
            rows.append(row)
            
        for row in rows:
            o += " ".join(row)
            o += "\n"
            
        return o
    
    def move_for_cpus(self):
        max_turns = self.game.player_set.filter(user__is_active=True).select_related('turn').annotate(turns=Count('turn')).aggregate(Max('turns'))
        
        for cpu in self.game.player_set.filter(user__is_active=False).all():
            print max_turns, cpu.turn_set.count()
            if max_turns['turns__max'] > cpu.turn_set.count():
                ai = AI(cpu)
                turn = ai.go()
    
    def serialize(self, player):
        game_dict = expand(self.game)
        game_dict['player'] = expand(player)
        game_dict['player']['cell'] = expand(player.playercell)
        game_dict['player']['user'] = expand(player.user)
        try: game_dict['player']['user']['profile'] = expand(player.user.get_profile())
        except: pass
            
        game_dict['players'] = [] 
        _players = self.game.player_set.all()
        
        for i in _players:
            _player = expand(i)
            _player['user'] = expand(i.user)
            _player['cell'] = expand(i.playercell)
            try: _player['user']['profile'] = expand(i.user.get_profile())
            except: pass
            game_dict['players'].append(_player)
        
        game_dict['clues'] = serialize_qs(player.clue_set.all())
        return game_dict
    
    def html(self, request):
        o = ""
        rows = []
        
        for y in range(0, self.game.board_size):
            row = []
            for x in range(0, self.game.board_size):
                extra_class = ""
                try:
                    player_here = self.game.player_set.get(x=x, y=y)
                    if request.user  == player_here.user:
                        extra_class = "you"
                    row.append('<td class="occupied %s">%s</td>' % (extra_class, str(player_here.user.username[:4])))
                except ObjectDoesNotExist:
                    row.append("<td></td>")
                except:
                    traceback.print_exc()
                
            rows.append('<tr>' + '\n'.join(row) + '</tr>')
            
        return '<table class="board" cellspacing="0" cellpadding="0" width="' + str(64*self.game.board_size) + '">' + '\n'.join(rows) + '</table>'   
        
class AI(object):
    actions = ('move', 'investigate', 'guess')
    log = get_logger('ai')
    
    def __init__(self, player):
        self.player = player
        self.game = player.game
        
    def go(self):
        import random
        _action = random.randint(0, 0)
        action = self.actions[_action]

        try:
            action_function = getattr(self, action)
            turn = action_function()
            if not turn:
                self.log.info('%s failed to %s, so moving instead.')
                return self.move()
            else:
                self.log.info(turn)
                return turn
        except:
            raise ValueError("Invalid action: %s" % action)
        
    def move(self):
        ideas = ('left', 'right', 'down', 'up')
        
        for idea in ideas:
            try:
                self.player.move(idea)
                cpu_turn = Turn(player=self.player, action='move', params=idea)
                cpu_turn.save()
                return cpu_turn
            except:
                traceback.print_exc()
                pass
        
    def guess(self):
        to_investigate = game.get_players_within(self.player.x, self.player.y, 1).exclude(pk=self.player.id).order_by('?')
        if to_investigate:
            new_clue = self.player.investigate(to_investigate)
            print new_clue
            
        else:
            print "no one to investigate"
        pass
    
    def investigate(self):
        pass    