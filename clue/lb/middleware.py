import traceback, sys
from django.db import connection
from django.conf import settings
import util
        
class ConsoleExceptionMiddleware:
    def process_exception(self, request, exception):
        exc_info = sys.exc_info()
        print "######################## Exception #############################"
        print '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
        print "################################################################"

class RequestDebugMiddleware:
    def process_request(self, request):
        print request.META['PATH_INFO']
        
        for i in request.POST:
            print request.POST[i]
        
        print request.user
        #print request.META
        
        for header in ['HTTP_AUTHORIZATION']:
            try:
                print reqeust.META[header]
            except:
                pass
        

#Log queryies longer than this
SLOW_QUERY_TIME = 0.5
LOG_NAME = 'sql'
DEBUG = getattr(settings, 'DEBUG', True)

class SlowQueryLogMiddleware(object):
    def __init__(self):
        self.log = util.get_logger(LOG_NAME)
        
    """
    Logs queryies that take longer than SLOW_QUERY_TIME
    Logs total time and query count
    """
    def process_response(self, request, response):
        total_time = 0.0
        self.log.info(request.method + " - " + request.get_full_path())
        if DEBUG:
            print "-"*80, "\n", request.method + " - " + request.get_full_path(), "\n", "-"*80
        
        for query in connection.queries:
            if DEBUG: print query['sql'], query['time'], '\n\n'
            total_time += float(query['time'])
            
            if float(query['time']) >= SLOW_QUERY_TIME: 
                _log = "[%s] %s" % (query['sql'], query['time'])
                self.log.info(_log)
                    
        self.log.info("[Queries: %d, Time: %s seconds]" % (len(connection.queries), total_time))
        return response

