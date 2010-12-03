def ip_address_processor(request):
    return {'ip_address': request.META['REMOTE_ADDR']}

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def media_url():
    return getattr(settings, 'MEDIA_URL', None)