import traceback, exceptions, random, time
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Max, Min, Sum
from django.core.cache import cache
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
    turn_window = 10
    cpu_window = 10
    log = get_logger('game')
    
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
                
                pc_fact= CellFact(
                    cell = player.playercell,
                    player = other,
                    neg = True,
                    game = self.game
                )
                pc_fact.save()
                pc_clue = Clue(
                    fact = pc_fact,
                    player = player,
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
    
    def is_over(self):
        human_players = self.game.player_set.filter(user__is_active=True).all()
        unkown_facts = 0
        for human in human_players:
            unkown_facts += human.unkown_facts()
            
        if unkown_facts == 0 and self.game.is_current:
            self.endgame()
            
        return unkown_facts == 0
    
    def endgame(self):
        self.game.is_current = False
        try:
            self.game.end = datetime.datetime.now()
        except:
            pass
        self.game.save()
        
        guesses = Guess.objects.filter(player__in=self.game.player_set.all()).order_by('created')
        guesses_per_player = {}
        
        for guess in guesses.all():
            if guess.other_player.id not in guesses_per_player:
                guesses_per_player[guess.other_player.id] = 1
            else:
                guesses_per_player[guess.other_player.id] += 1
            guess.points = self.game.player_set.count() - guesses_per_player[guess.other_player.id]
            guess.save()
            
        self.game.ranking_set.all().delete()
            
        for player in self.game.player_set.all():
            
            if player.is_current:
                endgame_alert = Alert(
                    player = player,
                    type = "message",
                    text = "The game is over"
                )
                endgame_alert.save()
                
            total_points = Guess.objects.filter(player=player, points=None).annotate(total_points=Sum('points')).aggregate(Sum('points'))
            
            player.ranking = Ranking(
                total_points = total_points['points__sum'],
                game = self.game
            )
            player.ranking.save()
            player.is_current = False
            player.save()
            
        i = 0
        for ranking in self.game.ranking_set.order_by('-total_points').all():
            ranking.rank = i
            ranking.save()
            i+=1
            
    
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
        max_turn_id = Turn.objects.filter(player__id__in=self.game.player_set.all()).aggregate(Max('id'))['id__max']
        
        if not self.get_cached('max_turn_id'): self.set_cached('max_turn_id', max_turn_id)
        elif max_turn_id < self.get_cached('max_turn_id'):
            print "not updating, still on turn: %d" % (max_turn_id)
            return
        
        max_turns = self.get_cached('max_turns')
        min_turns = self.get_cached('min_turns')

        if not max_turns:
            max_turns = self.game.player_set.filter(is_current=True).select_related('turn').annotate(turns=Count('turn')).aggregate(Max('turns'))['turns__max']
            self.set_cached('max_turns', max_turns)
        
        if not min_turns:
            min_turns = self.game.player_set.filter(is_current=True).select_related('turn').annotate(turns=Count('turn')).aggregate(Min('turns'))['turns__min']
            self.set_cached('min_turns', min_turns)
        
        #For each CPU
        for cpu in self.game.player_set.filter(user__is_active=False).all():
            cpu_turns = cpu.turn_set.count()
            if cpu_turns is None: cpu_turns = 0
            #If the cpu has less turns than the maximum active player, move
            if not max_turns or cpu_turns < max_turns + self.cpu_window:
                ai = AI(cpu)
                turn = ai.go()
              
    def in_window(self, player):
        player_turns = player.turn_set.count()
        
        if player_turns > self.get_cached('min_turns') + self.turn_window:
            return True
        
        return False
    
    def turns_allowed(self, player):
        min_turns = self.get_cached('min_turns')
        if not min_turns: min_turns = 0
        return self.turn_window - (player.turn_set.count() - min_turns)
                
    def get_cached(self, field, timeout=20):
        cached = cache.get('game_%d_%s' % (self.game.id, field))
        try:
            time.time() - int(cached['t'])
        except:
            pass
        if cached is None:
            return None
        if 'v' in cached and timeout > (time.time() - int(cached['t'])):
            self.log.info("memcached hit: %s=%s" % (field, cached['v']))
            return cached['v']
        else:
            return None
    
    def set_cached(self, field, value):
        self.log.info( "memcached set: %s=%s" % (field, value))
        return cache.set('game_%d_%s' % (self.game.id, field), {'t': int(time.time()),'v': value})
        
    def serialize(self, player):
        game_dict = expand(self.game)
        game_dict['player'] = expand(player)
        game_dict['player']['cell'] = expand(player.playercell)
        game_dict['player']['cell']['player_id'] = player.id
        game_dict['player']['user'] = expand(player.user)
        game_dict['player']['unkown_facts'] = player.unkown_facts()
        """
        try:
            game_dict['player']['user']['profile'] = expand(player.user.get_profile())
        except:
            pass
        """
        
        game_dict['players'] = [] 
        _players = self.game.player_set.select_related('user', 'cell').all()
        
        for i in _players:
            _player = expand(i)
            _player['user'] = expand(i.user)
            _player['role'] = expand(i.playerrole.role)
            _player['cell'] = expand(i.playercell)
            _player['cell']['player_id'] = i.id
            _player['unkown_facts'] = i.unkown_facts()
            """
            try: _player['user']['profile'] = expand(i.user.get_profile())
            except: pass
            """
            game_dict['players'].append(_player)
        
        game_dict['clues'] = serialize_qs(player.clue_set.all())
        game_dict['turns'] = {
            'min': self.get_cached('min_turns'),
            'max': self.get_cached('max_turns'),
            'max_turn_id': self.get_cached('max_turn_id')}
        game_dict['correct_guesses'] = serialize_qs(player.guess_set.filter(correct=1))
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