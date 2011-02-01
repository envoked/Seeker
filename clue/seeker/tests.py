from datetime import datetime
import random, traceback, curses
from sys import stdout
from django.test import TestCase
from django.contrib.auth.models import *
from seeker.models import *
from seeker.games import *

class GameTest(TestCase):
    fixtures = ['auth.json', 'seeker.json']
    num_players = 4
    
    def test_boardgame(self):
        human_players = int(raw_input("How many humans"))
        cpu_players = int(raw_input("How many cpus"))
        human_users = User.objects.filter(is_active=True).all()[:human_players]
        cpu_users = User.objects.filter(is_active=False).all()[:cpu_players]
        
        game = Game(
            start = datetime.datetime.now(),
            board_size = human_players + cpu_players
        )
        game.save()
    
        for user in human_users:        
            player = Player(
                user = user,
                game = game
            )
            player.save()
            
        for user in cpu_users:        
            player = Player(
                user = user,
                game = game
            )
            player.save()
        
        bg = BoardGame(game)
        key_codes = {"\x1b[D": 'left', '\x1b[A': 'up', "\x1b[C": 'right', "\x1b[B": 'down'}
        
        controls = """Controls:
        m: move
        i: investigate player next to you
        g: guess a player's role
        s: skip
        """
        print controls
        
        while True:
            """
            Continue from this control stucture if cpus should get a turn
            """
            for player in game.player_set.all():
                print '-'*20
               
                if player.can_guess_without_deduction():
                    print "%s knows everything!" % player.playerrole
                    raw_input()
                    continue
                
                if not player.user.is_active:
                    #cpus cannot move yet, so let them see 5 spaces
                    to_investigate = game.get_players_within(player.x, player.y, 5).exclude(pk=player.id).order_by('?')
                    if len(to_investigate) > 0:
                        to_investigate = to_investigate[0]
                        player.investigate(to_investigate)
                        print "%s investigated %s" % (player.playerrole.role, to_investigate.playerrole.role)
                else:
                    _clear()
                    raw_input("Pass the computer to %s and press RETURN" % player.user.username)
                    _clear()
                    print "You are playing as: %s" % player.user.username
                    print "You role is: %s (abbreviated as %s)" % (player.playerrole.role.name, player.playerrole.role.name[0])
                    print '-'*20
                    print "Your clues"
                    print '-'*20
                    print player.explain_clues()
                    print bg.console_display()
                    print controls

                    action = raw_input(">")
                    
                    if action == 'm':
                        move = raw_input("Move:")
                        try:
                            player.move(key_codes[move])
                        except:
                            traceback.print_exc()
                            continue
                    
                    elif action == 'g':
                        known_facts = player.clueownership_set.filter(clue__fact__neg=False).values('clue__fact__player')

                        for p in game.other_players(player).exclude(id__in=known_facts).all():
                            print p.playerrole.role.name + ": %d" % p.id
                        
                        _guessed = raw_input("Who would you like guess the identity of?:")
                        try:
                            guessed = game.player_set.get(id=_guessed)

                            for p in game.other_players(player).exclude(id__in=known_facts).all():
                                print p.user.username + ": %d" % p.user.id
                            _user = raw_input("What is thier user?:")    
                            try:
                                user = User.objects.get(id=_user)
                                correct = bg.guess(user, guessed.playerrole.role)
                                if correct:
                                    print "You are correct!"
                                    rf = RoleFact(player=user.player_set.get(is_current=True), neg=False, role=guessed.playerrole.role)
                                    rf.save()
                                    new_positive_clue = Clue(
                                        fact = rf,
                                        game=game
                                    )
                                    new_positive_clue.save()
                                    player.clueownership_set.add(ClueOwnership(clue=new_positive_clue))
                                else:
                                    print "You are wrong!"
                                    rf = RoleFact(player=user.player_set.get(is_current=True), neg=True, role=guessed.playerrole.role)
                                    rf.save()
                                    new_negative_clue = Clue(
                                        fact = rf,
                                        game=game
                                    )
                                    new_negative_clue.save()
                                    player.clueownership_set.add(ClueOwnership(clue=new_negative_clue))
                            except:
                                traceback.print_exc()
                        except:
                            traceback.print_exc()
                            
                    elif action == 'i':
                        neighbors = game.get_players_within(player.x, player.y, 1).exclude(pk=player.id).all()
                        if len(neighbors) == 0:
                            print "You have no neighbors"
                        
                        for p in neighbors:
                            print p.playerrole.role.name + ": %d" % p.id
                            
                        _investigated = raw_input("Who would you like to investigate:")
                        try:
                            player_investigated = game.player_set.get(id=_investigated)
                            new_clue = player.investigate(player_investigated)
                            if new_clue:
                                print "\nYou learned:"
                                print new_clue
                            else:
                                print "%s knows nothing that you don't" % player_investigated.playerrole.role.name
                                
                            print "\nEverything you know:"
                            print player.explain_clues()
                        except:
                            traceback.print_exc()
                            continue
                    elif action == 's':
                        pass
                    else:
                        print controls
                        
                    raw_input("Press ANY KEY")
                
                

def _clear():
    curses.setupterm()
    stdout.write(curses.tigetstr("clear"))
    stdout.flush()