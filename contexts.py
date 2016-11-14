def appname(request):
    return {'appname': request.resolver_match.app_name }

def urlname(request):
    return {'urlname': request.resolver_match.url_name }

