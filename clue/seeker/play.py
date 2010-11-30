from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from lobby.models import *
from lobby import *
from games import *
from lb.util import expand

NUM_PLAYERS = 4

@login_required
@render_to('game.html')
def game(request, game_id):
    #404 for invalid game
    game = get_object_or_404(Game, id=game_id)
    #404 if user is not a player in game
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )

    context = {
        'game': game,
        'player': player
    }

    return context

@render_to('play.html')
def debug_clues(request, game_id):
    game = Game.objects.get(id=game_id)

    context = {
        'game': game
    }

    return context


@render_to('guesser.html')
def guesser(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if not game.is_current:
        return HttpResponseRedirect('/seeker/game/%s/' % game.id)
    
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    roles = PlayerRole.objects.filter(player__in=game.player_set.all()).exclude(role=player.playerrole.role)
    other_players = game.player_set.exclude(user=request.user)

    context = {
        'game'  : game,
        'player': player,
        'roles' : roles,
        'other_players': other_players
    }
    return context

def guess(request, game_id):
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
    player = Player.objects.get(
        user = request.user,
        game = game,
        is_current = True,
    )
    player.is_current = False
    player.save()
    return HttpResponseRedirect('/lobby/home/')

