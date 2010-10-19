from datetime import datetime, timedelta
from django.contrib import auth
from django.http import *
from django.shortcuts import render_to_response,  get_object_or_404
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import *
from lobby import *
from lobby.models import *


def send_message(request):
    to = User.objects.get(request.REQUEST['to'])
    sender = request.user
    content = request.REQUEST['content']
    
    new_message = Message(
        sender=sender,
        to = to,
        content = content
    )
    new_message.save()
    return HttpResponse()
    
def get_messages(request):
    messages = Message.objects.filter(to=request.user)
    
    return HttpResponse(str(messages.values()))