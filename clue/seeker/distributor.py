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