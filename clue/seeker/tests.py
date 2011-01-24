from datetime import datetime
import random, traceback
from django.test import TestCase
from django.contrib.auth.models import *
from seeker.models import *
from seeker.games import *

class GameTest(TestCase):
    fixtures = ['auth.json', 'seeker.json']
    num_players = 4
    
    def test_boardgame(self):
        from django.db import connections
        conn = connections.all()[0]

        users = User.objects.filter(is_active=True).all()
        
        game = Game(
            start = datetime.datetime.now(),
            board_size = users.count()-1
        )
        game.save()
        users = users[1:]
    
        for user in users:        
            player = Player(
                user = user,
                game = game
            )
            player.save()
        
        bg = BoardGame(game)
        player = game.player_set.all()[0]
        cpus = game.player_set.exclude(pk=player.id).all()
        print "You are playing as: %s" % player.user.username
        print "You role is: %s (abbreviated as %s)" % (player.playerrole.role.name, player.playerrole.role.name[0])
        key_codes = {"\x1b[D": 'left', '\x1b[A': 'up', "\x1b[C": 'right', "\x1b[B": 'down'}
        
        controls = """Controls:
        m: move
        c: show what players know
        i: investigate player next to you
        g: guess a player's role
        s: skip
        """
        print controls
        
        while True:
            """
            Continue from this control stucture if cpus should get a turn
            """
            print bg.console_display()
            action = raw_input(">")
            
            if action == 'm':
                move = raw_input("Move:")
                try:
                    player.move(key_codes[move])
                except:
                    traceback.print_exc()
                    continue
            elif action == 'c':
                print '-'*20
                print "Your clues"
                print '-'*20
                print player.explain_clues()
                
                for p in cpus:
                    print '-'*20
                    print p.explain_clues()
                    continue
                    
            elif action == 'i':
                neighbors = game.get_players_within(player.x, player.y, 1).all()
                if len(neighbors) == 0:
                    print "You have no neighbors"
                    continue
                
                for p in neighbors:
                    print p.playerrole.role.name + ": %d" % p.id
                    
                _investigated = raw_input("Who would you like to investigate:")
                try:
                    player_investigated = game.player_set.get(id=_investigated)
                    new_clue = player.investigate(player_investigated)
                    if new_clue:
                        print "You learned:"
                        print new_clue
                    else:
                        print "%s knows nothing that you don't" % player_investigated.playerrole.role.name
                        
                    print "Everything you know:"
                    print player.explain_clues()    
                except:
                    traceback.print_exc()
                    continue
            elif action == 's':
                pass
            else:
                print controls
                continue
            
            """
            Very basic AI
            """
            for cpu in cpus:
                if cpu.can_guess_without_deduction():
                    print "%s knows everything!" % cpu.playerrole
                #cpus cannot move yet, so let them see 5 spaces
                to_investigate = game.get_players_within(cpu.x, cpu.y, 5).exclude(pk=cpu.id).order_by('?')
                if len(to_investigate) > 0:
                    to_investigate = to_investigate[0]
                    cpu.investigate(to_investigate)
                    
                    if to_investigate == player:
                        print "%s investigated you!" % (cpu.playerrole.role)
                    else:
                        print "%s investigated %s" % (cpu.playerrole.role, to_investigate.playerrole.role)
                
                