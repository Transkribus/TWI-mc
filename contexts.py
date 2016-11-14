def appname(request):
    return {'appname': request.resolver_match.app_name }

def funcname(request):
    return {'appname': request.resolver_match.func }

