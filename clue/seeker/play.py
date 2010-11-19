from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
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
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    roles = PlayerRole.objects.filter(player__in=game.player_set.all()).exclude(role=player.playerrole.role)
    other_players = game.player_set.exclude(user=request.user)
    print roles
    context = {
        'game'  : game,
        'player': player,
        'roles' : roles,
        'jquery': True,
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

    for guess in guesses:
        (other_player_id, role_id) = guess.split('=')
        other_player = Player.objects.get(id=other_player_id)
        role = Role.objects.get(id=role_id)
        
        try:
            guess = RoleGuess.get(player=player, other_player=other_player)
        except:
            guess = RoleGuess(
                player = player,
                other_player = other_player    
            )
        
        guess.role = role
        guess.save()
        
    winner = game.check_for_winner()
    return HttpResponse(json.dumps(expand(winner)))
    
    
def quit(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    player.delete()
    return HttpResponseRedirect('/lobby/home/')

