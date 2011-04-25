from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def display_role(value):
    html = '<span class="role" style="background-color: #%s">%s</span>' % (value.color, value.name)
    return mark_safe(html)
   
@register.filter 
def display_cell(cell):
    html = '<span class="cell">%d, %d</span>' % (cell.x+1, cell.y+1)
    return mark_safe(html)
