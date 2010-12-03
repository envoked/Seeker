from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
import smtplib
import traceback
from seeker.distributor import *

from django.core.management.base import *

class Command(NoArgsCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Sends Clues to Players'

    def handle_noargs(self, **options):
        self.stdout.write("SENDING CLUES\n")
        send_time_clues()   

