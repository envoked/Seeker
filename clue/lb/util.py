#!/usr/bin/env python
import logging
from django.conf import settings
from datetime import datetime, date
import traceback

def get_logger(filename):
    LOG = logging.getLogger(filename)
    LOG.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    hn = logging.FileHandler(settings.LOGGING_PATH + filename + ".log")
    LOG.addHandler(hn)
    hn.setFormatter(formatter)
    return LOG

def require_fields(request, fields):
    """
    Does the request have all required fields?
    Return True is so, (False, missing_fields) if not
    @return bool Valid, [] fields 
    """
    missing_fields = []
    for field in fields:
        try:
            val = request.REQUEST[field]
            print val
        except:
            missing_fields.append(field)
            
    if len(missing_fields) > 0: return (False, missing_fields)
    else: return (True, [])
    

def expand(row):
    """
    Serializes a model instance
    @return dict
    """
    expanded = {}
    for field in row.__class__._meta.fields:
        if type(field).__name__ == 'OneToOneField':
            continue
        
        if type(field).__name__ != 'ForeignKey':
            field_value = getattr(row, field.name)
 
        if type(field_value).__name__ in ['datetime', 'date']:
            field_value = datetime.strftime(field_value, "%Y-%m-%d %H:%M:%S")
        elif type(field).__name__ == 'ForeignKey':
            """
            LB ugly ugly, but asking for ForeignKey.id does a query, see http://groups.google.com/group/django-users/browse_thread/thread/76abaa0a373ac973
            """
            field_value = getattr(row, field.name + '_id')
        elif field_value == None:
            #Tony wants 0 instead of null or false
            field_value = 0
        elif type(field_value).__name__ == 'bool':
            field_value = int(field_value)
        elif type(field_value).__name__ in ['ImageFieldFile', 'FieldFile']:
            field_value = field_value.url
        elif type(field_value).__name__ == 'HTTPError':
            field_value = 0
        
        expanded[field.name] = field_value
    return expanded
    #LB - Lets Hold off on this until we finalize how were treating each type
    #return
    
def serialize_qs(qs, related=[]):
    seq = []
    for i in qs:
        row = expand(i)
        for r in related:
            if len(r.split('.')) == 2:
                a, b = r.split('.')
                first = getattr(i, a)
                row[a] = expand(first)
                row[a][b] = expand(getattr(first, b))
            else:
                row[r] = expand(getattr(i, r))
        seq.append(row)
    return seq
    
def model_values(row):
    fields = row.__class__._meta.fields
    _values = {}
    print fields
    for field in fields:
        try:
            _values[field] = getattr(row, field)
        except:
            traceback.print_exc()
            pass
        
    print _values
    return _values


def sanitize_row(row):
    from datetime import datetime, date
    for field in row:
        print field
        if type(row[field]).__name__ in ['datetime', 'date']:
            row[field] = datetime.strftime(row[field], "%Y-%m-%d %H:%M:%S")
            
    return row

from django.http import HttpResponseServerError

class AJAXSimpleExceptionResponse:
    def process_exception(self, request, exception):
        if settings.DEBUG:
            if request.is_ajax():
                import sys, traceback
                (exc_type, exc_info, tb) = sys.exc_info()
                response = "%s\n" % exc_type.__name__
                response += "%s\n\n" % exc_info
                response += "TRACEBACK:\n"    
                for tb in traceback.format_tb(tb):
                    response += "%s\n" % tb
                return HttpResponseServerError(response)