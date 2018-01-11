from django import template
from django.template.defaulttags import register
from django.utils.safestring import mark_safe
import datetime
import settings
from apps.utils.utils import error_message_switch, t_log, crop_as_imagemap, check_edit, get_wf
import logging
import os.path


#register = template.Library()
@register.filter
def print_timestamp(timestamp):
    try:
        #assume, that timestamp is given in seconds with decimal point
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts/1000.0)

#register.filter(print_timestamp)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def coords_for_fimagestore(crop):
    return str(crop.get('x'))+"x"+str(crop.get('y'))+"x"+str(crop.get('w'))+"x"+str(crop.get('h'))

@register.filter
def coords_add_commas(coords):
    return coords.replace(" ",",")

@register.filter
def coords_for_imagemap(crop):
    return ','.join([str(c) for c in crop_as_imagemap(crop)])

@register.filter
def y_for_typewriterline(crop):
    return str(crop.get('tl')[1])

@register.filter
def load_lib(lib,lib_type):
    tags = {'css' : '<link href="%s" rel="stylesheet"/>', 'js' : '<script src="%s"></script>'}
    
    if settings.USE_CDNS and lib in settings.CDNS:
        return  mark_safe(tags[lib_type] % str(settings.CDNS.get(lib).get('cdn')))
   
    local_lib_path = settings.PROJECT_ROOT+'/'+settings.STATIC_ROOT+'/'+settings.CDNS.get(lib).get('local')
    if os.path.isfile(local_lib_path) : 
        return  mark_safe(tags[lib_type] % str(settings.STATIC_PATH+settings.CDNS.get(lib).get('local')))

    t_log("Failed to load lib for local lib %s (%s)" %  (lib,local_lib_path), logging.WARN)
    t_log("IS IT EVEN A FILE? : %s" %  os.path.isfile(local_lib_path), logging.WARN)

    return '<!-- local lib not found with lib id %s at location %s -->' % (lib,local_lib_path)


@register.filter
def login_error_message(code):
    return error_message_switch(None,int(code))

#dates from transkribus are usually YYYY-MM-DD or similar YYYY-MM-DDTHH:MM:SS.SSS (2017-07-27T16:59:54.601)
@register.filter
def str_to_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.datetime.strptime(".".join(s.split('.')[:1]), "%Y-%m-%dT%H:%M:%S").date()
        except ValueError:
            return None

@register.filter
def intersect_and_first(c1,c2):
    c3 = [val for val in c1 if val in c2]
    return c3[0]

@register.filter
def thumb_from_page_url(page_url):
    return page_url.replace('view','thumb')

@register.filter
def add_one(n):
    return int(n)+1

@register.filter
def can_edit(role):
    return check_edit(role)

@register.filter
def get_workflow(role):
    return get_wf(role)

@register.filter
def get_workflow_statuses(role):
    return get_wf(role).get('statuses')

@register.filter
def opposite(mode):
    if mode == 'edit' : 
        return 'view'
    return 'edit'

@register.filter
def get_interfaces(mode):
    return settings.INTERFACES

