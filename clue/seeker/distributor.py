from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from lobby.models import *
from lobby import *
from games import *
import smtplib
import traceback
from random import *

CLUE_GENIE = "genie@seekr.us"

#Email a generic item...this will be changed to use google apps mail
def send_item(to, body):
    print body
    
    import smtplib
    server = smtplib.SMTP()
    server.connect('smtp.gmail.com')
    # identify ourselves, prompting server for supported features
    server.ehlo()
    # If we can encrypt this session, do it
    if server.has_extn('STARTTLS'):
        server.starttls()
        server.ehlo() # re-identify ourselves over TLS connection
        
    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    try:
        server.sendmail(settings.SMTP_USERNAME, [to], body)
    except:
        traceback.print_exc()
    server.quit()
    
    return HttpResponse("")
    

#Send the given clue to the appropriate player
def send_clue(clue):
    email = clue.player.user.email
    
    msg = """Intended Recipient: %s
Clue: %s
Intended Email: %s
    """ % (clue.player.user.username, str(clue.fact), email)
    
    self.stdout.write(msg)
    
    send_item(email, msg)
    
    clue.sent = 1
    clue.save()

def distribute_clues(target_game_id):
    #print target_game_id
    players = Player.objects.filter(game=target_game_id)
    num_players = players.count()
    game_clues = Clue.objects.filter(game=target_game_id, sent=0)[:num_players]
    
    #if there are no unsent clues
    if game_clues.count() == 0:
        print "NO REMAINING CLUES"
        return
    else:
        for clue in game_clues:
            send_clue(clue)
            
#sends a round of clues for all current games to all players in each game.
def send_time_clues():
    games = Game.objects.filter(is_current=1)
    print games
    for the_game in games:
        current_clues = Clue.objects.filter(game=the_game, sent=0, send_time__lt=datetime.now()).all()
        for clue_to_send in current_clues:
            print clue_to_send
            send_clue(clue_to_send)
          
#send the next clue for the given player, to that player
#will be used for non-global clue distribution
def send_clue_to_player(player):
    #a clue which has not been sent yet
    clue_to_send = Clue.objects.filter(player=player).exclude(sent=1).order_by('?')[0]
    send_clue(clue_to_send)

def exchange_clues(player1, player2):
    player1_clues_already_sent = []
    player2_clues_already_sent = []
    
    player1_facts = []
    player2_facts = []
    
    #get list of clues for each player which have already been sent and does not reference the other given player.
    player1_clues_already_sent = Clue.objects.filter(player=player1).exclude(sent=0)
    for clue1 in player1_clues_already_sent:
        if(clue1.fact.player_id != player2.id):
            player1_facts.append(clue1.fact)
    #    else:
    #        print clue1
    
    try:
        clue_to_send_player2_from_player1 = player1_facts[randint(0, len(player1_facts) - 1)]
    except ValueError:
        return
    
    
    player2_clues_already_sent = Clue.objects.filter(player=player2).exclude(sent=0)
    for clue2 in player2_clues_already_sent:
        if(clue2.fact.player_id != player1.id):
            player2_facts.append(clue2.fact)
    #    else:
    #        print clue2
    
    try:
        clue_to_send_player1_from_player2 = player2_facts[randint(0, len(player2_facts) - 1)]
    except ValueError:
        return
    
    print "CLUE FOR %s FROM %s" % (player1, player2)
    print clue_to_send_player1_from_player2
    
    print "CLUE FOR %s FROM %s" % (player2, player1)
    print clue_to_send_player2_from_player1
    
    

        
