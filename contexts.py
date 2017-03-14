from django import tempalte

def appname(request):
    return {'appname': request.resolver_match.app_name }

def urlname(request):
    return {'urlname': request.resolver_match.url_name }

def apphead(request):
    head_template = request.resolver_match.url_name+'/extra_head.html'
    try:
        template.loader.get_template(head_template) 
        return {'apphead' : head_template}
    except template.TemplateDoesNotExist:
        return {'apphead' : 'extra_head.html'} #fall back if no tempalte available


