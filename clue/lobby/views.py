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
from lb.util import expand

context = {
    'assets': settings.MEDIA_URL
}

@render_to('lobby/index.html')
def index(request):
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
    context['user'] = request.user
    
    if request.method == 'POST':
        new_lobby = Lobby(
            creator = request.user,
            name = request.POST['name']
        )
        new_lobby.save()
        return HttpResponseRedirect('/lobby/%d/' % new_lobby.id)
    else:
        context['create_lobby_form'] = CreateLobbyForm()
        
    return context
    
@login_required
@render_to('lobby/lobby.html')
def lobby(request, id):
    lobby = Lobby.objects.get(id=id)
    
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
    #return render_to_response(request, 'lobby/lobby.html', locals())
    
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
    

def login(request):
    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect("/lobby/join/")
            else:
                context['message'] = 'Your account has been disabled'
        else:
            context['message'] = 'Incorrect login'
    
    return render_to_response('lobby/login.html', context)
    
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/lobby')
    