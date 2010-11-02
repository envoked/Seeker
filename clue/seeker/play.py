from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from lobby.models import *
from lobby import *
from games import *

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