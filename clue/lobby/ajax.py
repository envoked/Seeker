from datetime import datetime, timedelta
from django.contrib import auth
from django.http import *
from django.shortcuts import render_to_response,  get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import *
from lobby import *
from lobby.models import *
from lb.util import *
from seeker.distributor import *

@login_required
def send_message(request):
    to = User.objects.get(id=request.REQUEST['to'])
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    sender = request.user
    content = request.REQUEST['content']
    
    new_message = Message(
        sender=sender,
        to=to,
        content=content,
        lobby=lobby
    )
    new_message.save()
    return HttpResponse()

@login_required
def get_messages(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    messages = Message.objects.filter(to=request.user).filter(lobby=lobby).select_related('user').all()

    out = serialize_qs(messages, related=['sender'])
    return HttpResponse(json.dumps(out))
    
@login_required
def get_members(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    members = lobby.members.all()
    print "get_members"
    print members
    out = serialize_qs(members, related=['user'])

    return HttpResponse(json.dumps(out))
    
def get_lobby(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    
    resp = expand(lobby)
    #print "get_lobby"
    #print resp
    resp['members'] = serialize_qs(lobby.members.all(), related=['user'])
    #print "123"
    return HttpResponse(json.dumps(resp))
    
@login_required
def add_cpu_user(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    members = lobby.members.all()
    user_ids = []
    
    for member in members:
        user_ids.append(member.user.id)
    
    user = User.objects.filter(is_active=False).exclude(id__in=user_ids)[0]
    
    cpu_member = Member(
        user = user,
        lobby = lobby,
        image = Lobby.default_cpu_image()
    )
    cpu_member.save()
    
    return HttpResponse(json.dumps(expand(cpu_member)))

@login_required    
def pick_character(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    character = request.REQUEST['character']

    creator = Member.objects.get(id=lobby.creator_id)

    creator.set_player_image(character)
    creator.save()

    return HttpResponse("")


@login_required
def remove_member(request):
    member_id_to_remove = request.REQUEST['member_to_remove']
    member_to_remove = Member.objects.get(id=member_id_to_remove)
    member_to_remove.delete()
    
    return HttpResponse("")
    
@login_required
def invite_member(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    email_address = request.REQUEST['email']
    
    import util
    lobby_link = util.site_url(request) + '/lobby/%d/' % lobby.id
    
    body = """From: %s <%s>\nTo: Player <%s>\nSubject: \n\n
    You're invited to join the Seekr game '%s'.
    
    %s
    """ % (CLUE_GENIE, settings.SMTP_USERNAME, email_address, lobby.name, lobby_link)
    
    send_item(email_address, body)
    return HttpResponse("Success")


@login_required
@render_to('lobby/avatar_picker.html')
def show_character_picker(request, lobby_id):
    chars = Lobby.getCharImages()
    return {"char_images" : chars, "lobby_id" : lobby_id}