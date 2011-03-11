from django.core.management.base import BaseCommand, CommandError
from seeker.models import *
from seeker.games import *
from datetime import datetime

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes games that if now is greater then their end time'

    def handle(self, *args, **options):
        games = Game.objects.filter(end__lt=datetime.now(), is_current=True)
        
        for game in games.all():
            brg = BasicRoleGame(game)
            brg.create_rankings()    
        
            for player in game.player_set.all():
                player.is_current = False
                player.save()
        
        #self.stdout.write(str(games))