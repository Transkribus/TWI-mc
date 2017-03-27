import requests
#import urllib2
from django.conf import settings
import sys
#from . import settings
from django.core.urlresolvers import reverse,resolve
from apps.utils.utils import t_log
import logging

def get_nav(siblings,focus_id,sibling_id,sibling_content,focus=None):

# siblings = collections
#    focus = collection=None#
#    focus_id = collId
#    sibling_id = 'colId'
#    sibling_content = 'colName'

    prev=None
    prev_content=None
    next=None
    next_content=None
    stop_next=False
    for sibling in siblings:
        if stop_next:
            next=sibling.get(sibling_id)
            next_content=sibling.get(sibling_content)
            break
        if sibling.get(sibling_id) == int(focus_id):
            focus = sibling
            stop_next=True
        else :
            prev=sibling.get(sibling_id)
            prev_content=sibling.get(sibling_content)

    t_log("NEXT: %s PREV: %s " % (next,prev), logging.WARN)
    return {'focus' : focus,
		'nav_up_content': "Up to list of collections", #TODO dynamic
		'nav_next': next, 
		'nav_next_content': next_content,
		'nav_prev':prev,
 		'nav_prev_content': prev_content}

###below is deprecated

hierarchy = {'word': 'line',
             'line': 'region',
             'region': 'transcript',
             'transcript': 'page',
             'page': 'document',
             'document': 'collection',
             'collection': 'collections'}

def up_next_prev(request,this_level,this_id, data,parent_ids=None):

    up=prev=next=None
    up=[hierarchy.get(this_level)]
    up_content=hierarchy.get(this_level)
    if parent_ids:
        for id in parent_ids: #TODO work out slicker way to do this
            up.append(id)
    #assumptions are that we want to traverse by id and do that they will be presented to us in order (can sort data if not)
    next_promise=False
    last_id=None
    for x in data:
        that_id = x.get("key")
        if next_promise:
            next=that_id
            next_promise=False
        if str(that_id) == str(this_id):
            prev=last_id
            next_promise=True
        last_id = that_id

    return {#'nav_up': settings.APP_BASEURL+'/'.join(up),
		'up': resolve(request.path).app_name+'/'+'/'.join(up),
		'up_content': "Up to parent "+up_content,
                'next':next,
		'next_content': "Next "+this_level,
                'prev':prev,
		'prev_content': "Previous "+this_level}
