from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

try:
    import simplejson as json
except:
    import json

def render_to(template_name):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(template_name, output, context_instance=RequestContext(request))
        return wrapper
    return renderer

class CreateUserForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=30)
    email = forms.CharField(max_length=255)
    
class CreateLobbyForm(forms.Form):
    name = forms.CharField(max_length=255)
    
class SendMessageForm(forms.Form):
    content = forms.CharField(max_length=1000, widget=forms.Textarea)
    to = forms.ChoiceField(choices=(), required=False)
    lobby = forms.IntegerField(widget=forms.HiddenInput)
    