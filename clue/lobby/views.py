from datetime import datetime, timedelta
from django.contrib import auth
from django.http import *
from django.shortcuts import render_to_response,  get_object_or_404
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import *
from lobby import *
from lobby.models import *
from seeker.models import Player
from lb.util import expand
from forms import UserProfileForm
import traceback

context = {
    'assets': settings.MEDIA_URL
}

@render_to('lobby/index.html')
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/lobby/home/')
    return locals()

@login_required
@render_to('lobby/home.html')
def home(request):
    try:
        player = Player.objects.get(user=request.user, game__is_current=True, is_current=True)
        print player
    except:
        traceback.print_exc()
        player = None
    
    #show past games that have been closed and player has left
    history = Player.objects.filter(user=request.user, game__is_current=False, is_current=False)
    history = history.order_by('-game__end')[:5]
        
    return locals()

@login_required
@render_to('lobby/join.html')
def join(request):
    context['user'] = request.user
    one_hour_ago = datetime.datetime.now() - timedelta(hours=1)
    lobbies = Lobby.objects.filter(created__gte=one_hour_ago).all()
    
    context.update(locals())
    return context

@login_required
@render_to('lobby/create.html')
def create(request):
    if request.method == 'POST':
        create_lobby_form = CreateLobbyForm(request.POST)
        if create_lobby_form.is_valid():
            new_lobby = Lobby(
                creator = request.user,
                name = request.POST['name'],
                num_players = request.POST['num_players'],
                hours = request.POST['hours'],
                minutes = request.POST['minutes']
            )
            new_lobby.save()
            return HttpResponseRedirect('/lobby/%d/' % new_lobby.id)
    else:
        create_lobby_form = CreateLobbyForm()
        
    return locals()
    
@login_required
@render_to('lobby/lobby.html')
def lobby(request, id):
    lobby = get_object_or_404(Lobby, id=id, game=None)
    
    if request.user.is_authenticated():
        member = Member(
            lobby = lobby,
            user = request.user
        )
        try:
            member.save()
        except:
            pass
        
    send_message_form = SendMessageForm({'lobby': lobby.id, 'content':" "})
    lobby_json = json.dumps(expand(lobby))
    user_json = json.dumps(expand(request.user))
    return locals()

@login_required
@render_to('accounts/settings.html')
def settings(request):    
    original = {
        'email': request.user.email
    }
    
    if request.method == 'POST':
        settings_form = SettingsForm(request.POST)
        if settings_form.is_valid():
            user = request.user
            user.email = request.POST['email']
            user.save()
    else:
        settings_form = SettingsForm(original)
    
    return locals()
    
def start_game(request, lobby_id):
    """
    Turns a Lobby into a Game
    Can only be called once by the creator
    """
    one_hour = timedelta(hours=1)
    one_minute = timedelta(minutes=1)
    
    
    lobby = Lobby.objects.get(id=lobby_id)
    num_hours = lobby.hours
    
    num_minutes = lobby.minutes
    
    from seeker.models import Game, Player
    game = Game(
        start = datetime.datetime.now(),
        end = datetime.datetime.now() + (one_hour * num_hours) + (one_minute * num_minutes),
        creator = lobby.creator
    )
    game.save()

    for member in lobby.members.all():        
        player = Player(
            user = member.user,
            game = game
        )
        player.save()
    
    lobby.game = game
    lobby.save()
    
    from seeker.games import BasicRoleGame
    gameplay = BasicRoleGame(game)
    gameplay.process_players()
    game = gameplay.play()
        
    return HttpResponseRedirect('/seeker/game/%d/' % game.id)
    
def register(request):
    
    if request.method == 'POST':
        context['register_form'] = CreateUserForm(request.POST)
        if context['register_form'].is_valid():
            new_user = User.objects.create_user(
                email=request.POST['email'],
                username=request.POST['username'],
                password=request.POST['password']
            )
            new_user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, new_user)
            return HttpResponseRedirect('/lobby/')
    else:
        context['register_form'] = CreateUserForm()
    
    return render_to_response('lobby/register.html', context)

@login_required
@render_to('accounts/profile.html')
def profile(request):
    try:
        myprofile = request.user.get_profile()
    except:
        up = UserProfile(user=request.user)
        up.save()
        myprofile = request.user.get_profile()

    if request.method == 'POST':
        f = UserProfileForm(request.POST, request.FILES, instance=myprofile)
        if f.is_valid():
            f.save()
    else:
        f = UserProfileForm(instance=myprofile)

    return {'user_profile_form':f, 'profile':myprofile}


def login(request):
    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        print user
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                if 'next' in request.POST:
                    return HttpResponseRedirect(request.POST['next'])
                return HttpResponseRedirect("/lobby/")
            else:
                context['message'] = 'Your account has been disabled'
        else:
            context['message'] = 'Incorrect login'
    
    return render_to_response('lobby/login.html', context, RequestContext(context))
    
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
    