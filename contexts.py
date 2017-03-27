from django import template
import re
from .utils import t_log

def appname(request):
    t_log("APPNAME: %s " % (request.resolver_match.app_name))
    return {'appname': request.resolver_match.app_name }

def urlname(request):
    return {'urlname': request.resolver_match.url_name }

def apphead(request):
    t_log("HEAD_TEMPLATE: %s " % (request.resolver_match.app_name))
    head_template = request.resolver_match.app_name+'/extra_head.html'
    t_log("HEAD_TEMPLATE: %s " % (head_template))

    try:
        template.loader.get_template(head_template) 
    except template.TemplateDoesNotExist:
        return {'apphead' : 'extra_head.html'} #fall back if no template available

    return {'apphead' : head_template}

def nav_up(request):
    request.path
    nav_up = re.sub(r'\/[^\/]+$',"",request.path)
    return {'nav_up': nav_up }


