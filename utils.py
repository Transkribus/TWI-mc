import re
import sys
import datetime
import json
import hashlib
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from django.conf import settings
import logging

#t_log calls gets logger and calls logger.log, default level is INFO but can be overriden either by importing loggingto use a constant or just passing the appropriate int

#CRITICAL 50
#ERROR	  40
#WARNING  30
#INFO     20
#DEBUG    10
#NOTSET   0

def t_log(text,level=logging.INFO):

    logger = logging.getLogger('django')
    logger.log(level,text)

def get_ts_session(request) :
    # The session was given to the user when they authenticated (see backends.py)
    # We want to simpy return that TranskribusSession object unless some configuraion of django/transkribus expiration has gone on
    # To try and cover all bases we just check each thing that should have been bestowed to request.user when the user authenticated

    if request.user.is_authenticated():
        # django thinks we are logged in, #but request.user doesn't have tsdata, which suggests something is up, lets logout and start again
        if not hasattr(request.user,"tsdata") : 
            return HttpResponse(status=401)
        # django thinks we are logged in, #but request.user.tsdata doesn't have t, which suggests something is up, lets logout and start again
        if not hasattr(request.user.tsdata,"t"): 
            return HttpResponse(status=401)
        
        t = request.user.tsdata.t

    else:
        # An anonymous transkribus session don't expec too much 
        t = TranskribusSession()

    # You made this far? have a biscuit!
    return t


def t_gen_request_id(url,params,userid):
    ###### EXCEPTION ######
    # we will exlucde the params of fulldoc calls from being used in cacheid,
    # this is because TS is not *currently* paging any data in the fulldoc requests
    # paging is handled here in django so lets's not reqeust the fulldocs unnecessarily
    pattern = re.compile('^.*fulldoc$')
    t_log("regex result for url (%s): %s" % (url,pattern.match(url)))
    if pattern.match(url) : 
        t_log("USING %s FOR FULL DOC CACHE ID" % hashlib.md5((str(url)).encode('utf-8')).hexdigest())
        return hashlib.md5((str(url)).encode('utf-8')).hexdigest()
    ########################

    return hashlib.md5((str(url)+str(params)+str(userid)).encode('utf-8')).hexdigest()

###########################################################
# crop(list coords, boolean offset=None)
# turn polygon coords into rectangle coords or xywh if offset flag set
def crop(coords, offset=None):
   # coords = region.get("Coords").get("@points")
    points = coords.split()
    xmin=ymin=99999999 #TODO durh...
    xmax=ymax=0
    points = [list(map(int, point.split(','))) for point in points]
    #boo two loops! but I like this one above here...
    #TODO woops... I actually need this to give the x-off y-off width and height...
    for point in points:
        if point[1] > ymax : ymax=point[1]
        if point[1] < ymin : ymin=point[1]
        if point[0] > xmax : xmax=point[0]
        if point[0] < xmin : xmin=point[0]
    if offset:
        crop = {'x':xmin, 'y':ymin, 'w':(xmax-xmin), 'h': (ymax-ymin)}
    else:
        crop = {'tl':[xmin,ymin], 'tr': [xmax,ymin], 'br': [xmax,ymax], 'bl': [xmin,ymax]}

    return crop
##################################
# t_metadata(str custom_attr)

def quote_value(m):
    return ':"'+m.group(1)+'",'

def quote_property(m):
    return '"'+m.group(1)+'":'

def t_metadata(custom_attr):

    #transcript metadata for this page ie the pageXML
    if not custom_attr:
        return None
    #CSS parsing (tinycss or cssutils) wasn't much cop so css => json by homemade regex (gulp!)

    #TODO rationalise steps
    #t_log("### CSS: %s   \r\n" % (custom_attr) )
    custom_json = re.sub(r' {', ': {', custom_attr)
    #t_log("### JSON 0: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r'}', '},', custom_json)
    #t_log("### JSON 1: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r':([^,{:]+);', quote_value, custom_json)
    #t_log("### JSON 2: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r'([^,:{}\s]+):', quote_property, custom_json)
    custom_json = "{"+custom_json+"}"
    #t_log("### JSON 3: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r',}', '}', custom_json)
    #t_log("### JSON FINAL: %s   \r\n" % (custom_json) )

    t_metadata = json.loads(custom_json)

    t_log("### METADATA from CSS: %s   \r\n" % (t_metadata) )

    return t_metadata

def error_message_switch(request=None,x=0):
    return {
#        401: _('Transkribus session is unauthorised, you must <a href="'+request.build_absolute_uri(settings.SERVERBASE+"/logout/?next={!s}".format(request.get_full_path()))+'" class="alert-link">(re)log on to Transkribus-web</a>.'),
        401: _('Transkribus session is unauthorised, you must log on to Transkribus-web.'),
        403: _('You are forbidden to request this data from Transkribus.'),
        404: _('The requested Transkribus resource does not exist.'),
        500: _('A Server error was reported by Transkribus.'),
        503: _('Could not contact the Transkribus service, please try again later.'),
    }.get(x, _('An unknown error was returned by Transkribus: ')+str(x))

def collection_from_collections(collections,collection_id) :
    for collection in collections:
        if collection.get("colId") == int(collection_id):
            return collection

def get_role(request,collId) :
    t = get_ts_session(request)

    collections = t.collections(request)
    for collection in collections:
        if collection.get('colId') == int(collId) :
             return collection.get('role')

def crop_as_imagemap(crop):
    return [crop.get('tl')[0], 
		crop.get('tl')[1], 
		crop.get('tr')[0], 
		crop.get('tr')[1], 
		crop.get('br')[0], 
		crop.get('br')[1],
		crop.get('bl')[0], 
		crop.get('bl')[1]
	    ]

def check_edit(role):
    if role in settings.CAN_EDIT:
        return True
    return False

def get_wf(role):
    workflows = settings.WORKFLOWS

    for wf_id, wf in workflows.items() :
        if role in wf['perms'] :
            return wf
    
    #not sure? return a default
    return workflows['default']


