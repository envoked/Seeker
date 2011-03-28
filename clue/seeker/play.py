from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.safestring import SafeString
from django.utils import simplejson
from lobby.models import *
from lobby import *
from games import *
from lb.util import expand, serialize_qs

@login_required
@render_to('game.html')
def game(request, game_id):
    #404 for invalid game
    game = get_object_or_404(Game, id=game_id)
    bg = BoardGame(game)
    message = ""
    show_board = True
    
    #404 if user is not a player in game
    player = Player.objects.select_related('user', 'cell').get(user=request.user, game=game)
    
    if player.is_current == False:
        message = "You are no longer active in this game."
        show_board = False
    
    turn = Turn(
        player = player
    )        

    if request.method == 'POST':
        game_dict = {
            'complete': False
        }

        if bg.is_over():
            game_dict["complete"] = True

        if 'move' in request.POST:
            move_coords = request.POST['move']
            x, y = move_coords.split(',')
            print "NEW LOCATION %s , %s" % (x, y)
            print "PLAYER LOCATION %s , %s" % (player.x, player.y)  
            
            cells = game.get_player_cells_within(int(x), int(y), 0)
            if cells:
                #direction = player.get_direction_of_movement(x, y)
                #print "DIRECTION: %s" % direction

                cubicle = cells[0]
                cubicle_owner = cubicle.player
                new_clue = player.investigate_cell(cubicle)
                if new_clue:
                    alert = Alert(
                        player = player,
                        type = 'cubicle_clue',
                        content_type = ContentType.objects.get_for_model(Clue),
                        object_id = new_clue.id
                    )
                    alert.save()
                    game_dict['new_alerts'] = [expand(alert)]
                    
            try:
                player.move_to(x, y)
                turn.action = 'move'
                turn.params = move_coords
                game_dict['game'] = bg.serialize(player)
            except ValueError:
                print "Too late move: %s" % (move_coords)
        else:
            bg.move_for_cpus()
            
        if 'investigate' in request.POST:
            investigating_player_id = request.POST['investigate']
            investigating_player = Player.objects.get(id=investigating_player_id, game=game)
            new_clue = player.investigate(investigating_player)
            if new_clue:
                alert = Alert(
                    player = player,
                    type = 'investigate_clue',
                    content_type = ContentType.objects.get_for_model(Clue),
                    object_id = new_clue.id
                )
                alert.save()
                game_dict['new_alerts'] = [expand(alert)]
            
            turn.action = 'investigate'
            turn.params = investigating_player_id
                
        if turn.action:
            turn.save()
            
        game_dict['game'] = bg.serialize(player)
        alerts_now = player.alert_set.filter(viewed=None).count()
        cache.set('player_%d_alerts' % alerts_now, alerts_now)

        game_dict['unviewed_alerts'] = serialize_qs(player.alert_set.filter(viewed=None).all())
        game_dict['turns_allowed'] = bg.turns_allowed(player)
        
        return HttpResponse(simplejson.dumps(game_dict), content_type='application/json')
        
    context = {
        'game': game,
        'player': player,
        'show_board': show_board,
        'message': message
    }

    return context

@render_to('clues.html')
def clues(request, game_id):
    game = Game.objects.get(id=game_id)
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    context = {
        'player': player,
        'game': game
    }

    return context

@render_to('clues_for_player.html')
def clues_for_player(request, game_id):
    game = Game.objects.get(id=game_id)
    for_player = Player.objects.get(id=request.REQUEST['player'])
    print for_player
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    role_positive = RoleFact.objects.filter(fact__neg=False, clue__player=player, fact__player=for_player).all()
    cell_positive = CellFact.objects.filter(fact__neg=False, clue__player=player, fact__player=for_player).all()
    
    role_negative = RoleFact.objects.filter(fact__neg=True, clue__player=player, fact__player=for_player).all()
    cell_negative = CellFact.objects.filter(fact__neg=True, clue__player=player, fact__player=for_player).all()
    print "wetwetwtw"
    return locals()

    
@render_to('alerts.html')
def alerts(request, game_id):
    game = Game.objects.get(id=game_id)
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    
    return {
        'viewed_alerts': player.alert_set.filter(viewed__isnull=False).order_by('-created'),
        'unviewed_alerts': player.alert_set.filter(viewed=None).order_by('-created'),
    }
    
def alert_viewed(request, game_id):
    alert = Alert.objects.get(id=request.POST['id'])
    alert.viewed = datetime.datetime.now()
    alert.save()
    
    return HttpResponse("OK")
    
@render_to('guesser.html')
def guesser(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if not game.is_current:
        return HttpResponseRedirect('/seeker/game/%s/' % game.id)
    
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    other_player = Player.objects.get(id=request.POST['player'])

    #LB - facts/clues do not affect guesser options, now guesses do
    #known_facts = player.clue_set.filter(fact__neg=False).values('fact__player')
    correct_guesses = player.guess_set.filter(correct=True).values('other_player')
    roles = PlayerRole.objects.filter(player__in=game.player_set.all()).exclude(player__in=correct_guesses).exclude(player=player)
    other_players = game.player_set.exclude(id__in=correct_guesses).exclude(id=player.id)

    context = {
        'game'  : game,
        'player': player,
        'roles' : roles,
        'other_player': other_player,
        'other_players': other_players
    }
    return context

def guess(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = Player.objects.get(
        user = request.user,
        game = game
    )
    other_player = Player.objects.get(id=request.POST['player'])
    role = Role.objects.get(id=request.POST['role'])
    cell = PlayerCell.objects.get(id=request.POST['cell'])
    
    guess = Guess(
        player = player,
        other_player = other_player,
        role = role,
        cell = cell,
    )
    
    print "Guessing:", other_player.user.username
    print guess.other_player.playerrole.role, role
    print guess.other_player.playercell, cell
    
    if guess.other_player.playerrole.role == role and guess.other_player.playercell == cell:
        guess.correct = True
    else:
        guess.correct = False
    
    guess.save()
    
    alert = Alert(
        player = player,
    )
    alert.content_type = ContentType.objects.get_for_model(guess)
    alert.object_id = guess.id
    
    if guess.correct:
        alert.type = 'correct_guess'
    else:
        alert.type = 'wrong_guess'
        
    alert.save()
    
    turn = Turn(
        action = "guess",
        params = guess.id,
        player = player
    )
    turn.save()
    
    if player.unkown_facts() == 0 and player.is_current:
        print "Player finished: %s" % str(player)
        for other in game.player_set.exclude(pk=player.id).all():
            consolation_guess = other.guess_set.filter(other_player=player, correct=True).all()
            if len(consolation_guess) == 0:
                print "Giving consolation guess to %s" % str(other)
                consolation_guess = Guess(
                    player = other,
                    other_player = player,
                    correct = True,
                    points = 0,
                    role = player.playerrole.role,
                    cell = player.playercell,
                )
                consolation_guess.save()
        
        player.is_current = False
        player.x = player.playercell.x
        player.y = player.playercell.y
        player.save()
    
    return HttpResponse(simplejson.dumps(expand(guess)))
    
@render_to('game-complete.html')
def game_complete(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = Player.objects.get(
        user = request.user,
        game = game
    )
    
@render_to('debug_clues.html')
def debug_clues(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    clues = game.clue_set.filter(fact__neg=False).all()
    cellfacts = CellFact.objects.filter(neg=False, game=game).all()
    return locals()

#Below Not used 1 think

def _guess(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    guesses_str = request.REQUEST['guess']
    guesses = guesses_str.split(',')
    print guesses

    player = Player.objects.get(
        user = request.user,
        game = game
    )
    try:
        submission = Submission.objects.get(player=player)
    except:
        submission = Submission(
            player = player,
            game = game
        )
        submission.save()
    
    try:
        #lb - for debugging, in reality you shouldn't get to guess more than once
        submission.roleguess_set.all().delete()
    except:
        pass

    for guess in guesses:
        (other_player_id, role_id) = guess.split('=')
        other_player = Player.objects.get(id=other_player_id)
        role = Role.objects.get(id=role_id)
        
        guess = RoleGuess(
            other_player = other_player,
            role = role,
            submission = submission
        )
        
        guess.role = role
        guess.save()
    
    from seeker.games import BasicRoleGame
    brg = BasicRoleGame(game)
    brg.check_submission(submission)
    return HttpResponse("")
    
def guess_for_cpus(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    cpu_players = game.player_set.filter(user__is_active=False).all()
    
    from seeker.games import BasicRoleGame
    brg = BasicRoleGame(game)
    
    for player in cpu_players:
        other_players = game.player_set.exclude(user=player.user).all()
        roles = PlayerRole.objects.filter(player__in=game.player_set.all()).exclude(role=player.playerrole.role)
        
        try:
            submission = Submission.objects.get(player=player)
        except:
            submission = Submission(
                player = player,
                game = game
            )
            submission.save()
                
        try:
            #lb - for debugging, in reality you shouldn't get to guess more than once
            submission.roleguess_set.all().delete()
        except:
            pass
        
        for other_player in other_players:
            role = roles[0]
            roles = roles[:1]
            guess = RoleGuess(
                other_player = other_player,
                role = role.role,
                submission = submission
            )
            guess.save()
    
        brg.check_submission(submission)
            
    return HttpResponse("")
            
    
def quit(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    game.is_current = False
    game.save()
    
    player = Player.objects.get(
        user = request.user,
        game = game,
    )
    player.is_current = False
    player.save()
    return HttpResponseRedirect('/lobby/home/')

@render_to('notification.html')
def show_notification(request, text):
    text = text.replace("_", " ")
    return {"text" : text}
    
