import requests
#import urllib2
from django.conf import settings
import sys
#from . import settings
from django.core.urlresolvers import reverse,resolve
from apps.utils.utils import t_log

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
    t_log("########## RORY WOZ ERE #############");
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
