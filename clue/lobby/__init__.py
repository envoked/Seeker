from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

import django.utils.simplejson as json


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
    username = forms.CharField(max_length=13)
    password = forms.CharField(max_length=30)
    email = forms.CharField(max_length=255)
    
class SettingsForm(forms.Form):
    email = forms.EmailField(max_length=255)
    
difficulty_choices = (
    ('0', 'Easy'),
    ('1', 'Medium'),
    ('2', 'Hard')
)

num_players_choices = (
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12')
)

hour_choices = (
    (0, '-'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8')
)

min_choices = (
    (0, '-'),
    (5, '5'),
    (10, '10'),
    (30, '30'),
    (45, '45')
)
    
class CreateLobbyForm(forms.Form):
    name = forms.CharField(max_length=255)
    num_players = forms.ChoiceField(choices=num_players_choices)
    difficulty = forms.ChoiceField(choices=difficulty_choices)
    
class SendMessageForm(forms.Form):
    content = forms.CharField(max_length=1000, widget=forms.Textarea)
    to = forms.ChoiceField(choices=(), required=False)
    lobby = forms.IntegerField(widget=forms.HiddenInput)
    