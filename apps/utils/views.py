import logging

from urllib.parse import urlparse

from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from django.shortcuts import resolve_url

from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

from django.template.defaultfilters import linebreaksbr
from apps.querystring_parser.querystring_parser import parser

from apps.utils.decorators import t_login_required_ajax
from apps.utils.services import *
from apps.utils.utils import t_log, error_message_switch

from .forms import RegisterForm
from .models import TSData


class LoginWithCookie(LoginView):

    template_name = 'registration/login-with-cookie.html'

    def form_invalid(self, form):

        response = super(LoginWithCookie, self).form_invalid(form)

        try:
            response.delete_cookie('JSESSIONID', path='/', domain='transkribus.eu')
        except (ValueError, TypeError, AttributeError) as error:
            logging.error("%r", error)
        finally:
            return response

    def form_valid(self, form):

        # NOTE: super.form_valid is where user is authenticated
        response = super(LoginWithCookie, self).form_valid(form)

        try:
            self.set_cookie(self.request, response)
        except (ValueError, TypeError, AttributeError) as error:
            logging.error("%r", error)

        return response

    def set_cookie(self, request, response):

        user = self.request.user
        transkribus = user.tsdata

        # Set-Cookie: JSESSIONID=""; Domain=transkri…nly; Path=/TrpServer/; Secure
        response.set_cookie(
            'JSESSIONID', value=transkribus.sessionId,
            path='/TrpServer/', domain='transkribus.eu',
            httponly=False, secure=True)

def register(request):
#TODO this is generic guff need to extend form for extra fields, send reg data to transkribus and authticate (which will handle the user creation)

    return render(request, 'pages/register.html' )

    if request.user.is_authenticated(): #shouldn't really happen but...
#        return HttpResponseRedirect(request.build_absolute_uri('/library/'))
        return HttpResponseRedirect(request.build_absolute_uri(request.resolver_match.app_name))
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            try:
                t = request.user.tsdata.t
                t.register(request)
                return HttpResponseRedirect(request.build_absolute_uri(request.resolver_match.app_name))
                #tried out modal here and it is nice (but not really for registration)
#               messages.info(request, _('Registration requested please check your email.'))
#                return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
            except ValueError as err:
#               return render(request, 'registration/register.html', {'register_form': form} )
                #Why the f**k won't this redirect?!? TODO fix or try another method
                return HttpResponseRedirect(request.build_absolute_uri('/library/error'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    #Recpatch errors are not properly dislpayed by bootstrap-form... hmph
    return render(request, 'registration/register.html', {'register_form': form} )

def logout_view(request):
    
    if request.user.is_authenticated() :
        #invalidate the transkribu session (at transkribus.eu)
        if hasattr(request.user,'tsdata') :
            request.user.tsdata.t.invalidate()
            #remove the pickled session from the database
            TSData.objects.get(user=request.user).delete()
        #logout (as normal)
        logout(request)

    #do some redirectin'
    redirect_to = request.GET.get("next")
    if redirect_to is None:
        redirect_to = settings.LOGOUT_REDIRECT_URL

    if redirect_to:
        o = urlparse(redirect_to)
        t_log("NETLOC: %s" % (o.netloc), logging.WARN)
        # Security check -- don't allow redirection to a different host.
        if not (o.netloc and o.netloc != request.get_host()):
            return HttpResponseRedirect(redirect_to)


@t_login_required_ajax
def table_ajax(request,list_name,collId=None,docId=None,page=None,userId=None) :
    
    t_list_name=list_name
    params = {'collId': collId, 'docId': docId, 'page': page, 'userid' : userId} #userid can only be used to filter in context of a collection
    ####### EXCEPTION #######
    # list_name is pages we extract this from fulldoc
    if list_name == 'pages' :
        t_list_name = "fulldoc"
        params['nrOfTranscripts']=1 #only get current transcript
    #########################

    (data,count) = paged_data(request,t_list_name,params)
    if isinstance(data,HttpResponse):
        return data

    t = request.user.tsdata.t

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(data,HttpResponse):
        t_log("data request has failed... %s" % data)
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return data

    filters = {
                'actions' : ['time', 'colId', 'colName', 'docId', 'docName', 'pageId', 'pageNr', 'userName', 'type'],
                'collections' : ['colId', 'colName', 'description', 'nrOfDocuments', 'role'],
                'users' : ['userId', 'userName', 'firstname', 'lastname','email','affiliation','created','userCollection.role'], #NB roles in userCollection
                'documents' : ['docId','title', 'desc', 'author', 'nrOfPages'],
#               'pages' : ['pageId','pageNr','thumbUrl','status', 'nrOfTranscripts'], #tables
                'pages' : ['pageId','pageNr','imgFileName','thumbUrl','status'], #thumbnails
                'crowdsourcing' : ['colId', 'colName', 'description', 'nrOfDocuments', 'role'],
              }

    ####### EXCEPTION #######
    # Do the extraction of pages from fulldoc
    if list_name == 'pages' :
        data = data.get('pageList').get('pages')
        data = map(get_ts_status,data)
    #########################

    data_filtered = filter_data(filters.get(list_name),data)

    ####### EXCEPTION #######
    # We cannot request a paged list of pages by docid, so we must manage paging here
    if list_name == 'pages' :
        dt_params = parser.parse(request.GET.urlencode())
        nValues = int(dt_params.get('length')) if dt_params.get('length') else int(settings.PAGE_SIZE_DEFAULT)
        index = int(dt_params.get('start')) if dt_params.get('start') else 0
        #lame paging for pages for now...
        data_filtered = data_filtered[index:(index+nValues)]
    ##########################

    return JsonResponse({
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': data_filtered
        },safe=False)
    

def table_ajax_public(request,list_name,collId=None,docId=None,page=None,userId=None) :
    
    t_list_name=list_name
    params = {'collId': collId, 'docId': docId, 'page': page, 'userid' : userId} #userid can only be used to filter in context of a collection
    ####### EXCEPTION #######
    # list_name is pages we extract this from fulldoc
    if list_name == 'pages' :
        t_list_name = "fulldoc"
        params['nrOfTranscripts']=1 #only get current transcript
    #########################

    (data,count) = paged_data(request,t_list_name,params)
    if isinstance(data,HttpResponse):
        return data

    #RM In some cases we will be recieving requests for data from unauthenticated (anonymous) users (ie crowdsourcing etc) 
    if request.user.is_authenticated():
        t = request.user.tsdata.t 
    else:
        t = TranskribusSession()
    #t = request.user.tsdata.t
 

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(data,HttpResponse):
        t_log("data request has failed... %s" % data)
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return data

    filters = {
                'crowdsourcing' : ['colId', 'colName', 'description', 'nrOfDocuments', 'role'],
              }

    ####### EXCEPTION #######
    # Do the extraction of pages from fulldoc
    if list_name == 'pages' :
        data = data.get('pageList').get('pages')
        data = map(get_ts_status,data)
    #########################

    data_filtered = filter_data(filters.get(list_name),data)

    ####### EXCEPTION #######
    # We cannot request a paged list of pages by docid, so we must manage paging here
    if list_name == 'pages' :
        dt_params = parser.parse(request.GET.urlencode())
        nValues = int(dt_params.get('length')) if dt_params.get('length') else int(settings.PAGE_SIZE_DEFAULT)
        index = int(dt_params.get('start')) if dt_params.get('start') else 0
        #lame paging for pages for now...
        data_filtered = data_filtered[index:(index+nValues)]
    ##########################

    return JsonResponse({
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': data_filtered
        },safe=False)
    

def getTagsString(personCount, placeCount, dateCount, abbrevCount, otherCount):
    tagsString = ''
    if personCount > 0 or placeCount>0 or dateCount>0 or abbrevCount>0 or otherCount>0:
        tagsString += '<br/>Tags: '
    if personCount > 0:
        tagsString += '<br/>Persons (' + str(personCount) + ')'
    if placeCount > 0:
        tagsString += '<br/>Places (' + str(placeCount) + ')'
    if dateCount > 0:
        tagsString += '<br/>Dates (' + str(dateCount) + ')'
    if abbrevCount > 0:
        tagsString += '<br/>Abbrevs: (' + str(abbrevCount) + ')'
    if otherCount > 0:
        tagsString += '<br/>Others: (' + str(otherCount) + ')'
        
    return tagsString

#Fetch a single thumb url from the collection referenced
def collection_thumb(request, collId):

    t = request.user.tsdata.t
    documents = t.documents(request,{'collId': collId})
    if isinstance(documents,HttpResponse):
        return documents
    #grab first doc
    docId = next(iter(documents or []), None).get("docId")

    fulldoc = t.fulldoc(request,{'collId': collId, 'docId': docId})
    if isinstance(fulldoc,HttpResponse):
        return fulldoc

    pages = fulldoc.get('pageList').get("pages")
#    a = len(pages) // 2 #page from the middle?
    #maybe just grab first page?
    thumb_url = pages[0]['thumbUrl']

    return JsonResponse({
            'url': thumb_url
       },safe=False)


#Fetch a single thumb url from the document referenced
def document_thumb(request, collId, docId):
    import timeit
    
    t = request.user.tsdata.t

    fulldoc = t.document(request, collId, docId,-1)
    if isinstance(fulldoc,HttpResponse):
        return fulldoc
    
    pages = fulldoc.get('pageList').get("pages")
#    a = len(pages) // 2 #page from the middle?
    #maybe just grab first page?
    thumb_url = pages[0]['thumbUrl']

    return JsonResponse({
            'url': thumb_url
        },safe=False)

## not used
#Fetch a single thumb url from the document referenced
def page_img(request, collId, docId, page):
    import timeit
    t = request.user.tsdata.t
   
    fulldoc = t.document(request, collId, docId, page)
    if isinstance(fulldoc,HttpResponse):
        return fulldoc
    
    currPage = fulldoc.get('pageList').get("pages")[page]
#    a = len(pages) // 2 #page from the middle?
    #maybe just grab first page?
    img_url = currPage['url']

    return JsonResponse({
            'url': img_url
        },safe=False)

@t_login_required_ajax
def collection_recent(request, collId):
    t = request.user.tsdata.t
 
    recent = t.collection_recent(request,collId)
    if isinstance(recent,HttpResponse):
        return error_view(request,recent)

    return JsonResponse(recent,safe=False)
 
@t_login_required_ajax
def document_recent(request, docId):
    t = request.user.tsdata.t
 
    recent = t.document_recent(request,docId)
    if isinstance(recent,HttpResponse):
        return error_view(request,recent)

    return JsonResponse(recent,safe=False)
 
##########
# Helpers
##########

# paged_data:
#       - Handle common parameters for paging and filtering data
#       - Calls utils.services.t_[list_name] requests
#       - Some params must be passed in params (eg ids from url, typeId from calling function)
#       - Some params are set directly from REQUEST, but can be overridden by params (eg nValues)

def paged_data(request,list_name,params=None):

    #collect params from request into dict
    dt_params = parser.parse(request.GET.urlencode())
    t_log("DT PARAMS: %s" % dt_params, logging.WARN)
    if params is None: params = {}
    params['start'] = str(dt_params.get('start_date')) if dt_params.get('start_date') else None
    params['end'] = str(dt_params.get('end_date')) if dt_params.get('end_date') else None
    params['index'] = int(dt_params.get('start')) if dt_params.get('start') else 0
    #This filters all actions request to the first page which is dumb.
    #It is probably to catch cases where not supplying a page number results in an error
    #Excepting actions call for now
    if dt_params.get('page') :
        params['page'] = int(dt_params.get('page')) 
    elif list_name != 'actions' :
        params['page'] = 1
    else :
        params['page'] = None

    #NB dataTables uses length, transkribus nValues
    if 'nValues' not in params :
        params['nValues'] = int(dt_params.get('length')) if dt_params.get('length') else 0
        #params['nValues'] = int(dt_params.get('length')) if dt_params.get('length') else settings.PAGE_SIZE_DEFAULT

#    params['sortColumn'] = int(dt_params.get('length')) if dt_params.get('length') else None
#    params['sortDirection'] = int(dt_params.get('start')) if dt_params.get('start') else None

    #this is the way that datatables passes things in when redrawing... may do something simpler for filtering if possible!!
    if 'columns' in dt_params and list_name == "actions" and dt_params.get('columns').get(5).get('search').get('value'):
        params['typeId'] = int(dt_params.get('columns').get(5).get('search').get('value'))

    ########### EXCEPTION ############
    # docId is known as id when passed into actions/list as a parameter
    if  list_name == 'actions' : params['id'] = params['docId']
    ##################################

    #Get data
    t_log("SENT PARAMS: %s" % params, logging.WARN) 

    #RM In some cases we will be recieving requests for data from unauthenticated (anonymous) users (ie crowdsourcing etc) 
    if request.user.is_authenticated():
        t = request.user.tsdata.t 
    else:
        t = TranskribusSession()
    #t = request.user.tsdata.t
    
    data = eval("t."+list_name+"(request,params)")

    #Get count
    count=None
    #When we call a full doc we *probably* want to count the pages (we can't fo that with a /count call)
    if list_name not in ["fulldoc"]:
        count = eval("t."+list_name+"_count(request,params)")
    #In some cases we can derive count from data (eg pages from fulldoc)
    if list_name == "fulldoc" : #as we have the full page list in full doc for now we can use it for a recordsTotal
        count = data.get('md').get('nrOfPages')
    
    return (data,count)


def get_ts_status(x) :
    x['status'] = x.get('tsList').get('transcripts')[0].get('status')
    return x

def filter_data(fields, data) :

    #data tables requires a specific set of table columns so we filter down the actions
    filtered = []
    #I suspect some combination of filter/lambda etc could do this better...
    for datum in data:
        filtered_datum = {}
        for field in fields :
            ### sub field extraction basically we use the notation field.sub_field and try to crack the 
            ### sub_field value out of the field value which we assume is a dict or a list (with one thing in it)
            ### currently only used for userCollection.role but could be useful for other things
            if field.find(".") > -1 : #sub_field
                parts = field.split(".")
                #t_log("PARTS: %s" % parts, logging.WARN)
                parent = parts[0]
                sub_field = parts[1]
                p_data = datum.get(parent)
                #t_log("P_DATA: %s" % p_data, logging.WARN)
                if isinstance(p_data,list) : #it's a list
                    #t_log("Its a list", logging.WARN)
                    pd_value = p_data[0].get(sub_field) #for now we get the first thing in the list but...
                    #in time we may wish to do something like the below (the caveat being that we need something to match the list item we want)
                    '''
                    for pd in p_data :
                        if pd.get(#the match id) == datum.get(#the match id) :
                             pd_value = pd.get(sub_field)
                    '''
                elif isinstance(p_data,dict) :
                    #t_log("Its a dict %s: %s" % (sub_field, p_data.get(sub_field)), logging.WARN)
                    pd_value = p_data.get(sub_field)
                filtered_datum[parent+"_"+sub_field] = pd_value if pd_value else "n/a" #TODO this will n/a 0!!
            else : #normal fields processed as usual
                filtered_datum[field] = datum.get(field) if datum.get(field) else "n/a" #TODO this will n/a 0!!
        filtered.append(filtered_datum)

    return filtered
#error pages (where not handled by modals)
def error_view(request, response) : 
    t_log("Request %s, Response %s" % (request,response), logging.WARN)
    return error_switch(request,response.status_code)

def error_switch(request,x):
    t_log("SERVERBASE IS %s" % settings.SERVERBASE, logging.WARN);
    #If transkribus session becomes unauthorised we need to remove it from the userobject, so we don't get stuck in a 401 state for ever...
   # if x == 401 :
   #      TSData.objects.get(user=request.user).delete()
    if x == 401 and TSData and hasattr(request.user,'tsdata') :
         try :
             tsdata = TSData.objects.get(user=request.user)
             if tsdata is not None :
                 tsdata.delete()
         except :
             pass


    return {
        401: HttpResponseRedirect(request.build_absolute_uri(settings.SERVERBASE+"/login?error=401&next=".format(request.get_full_path()))),
        403: render(request, 'error.html', {
		'msg' : error_message_switch(request,403) }),
        404: render(request, 'error.html', {
		'msg' : error_message_switch(request,404) }),
        500: render(request, 'error.html', {
		'msg' : error_message_switch(request,500) }),
        503: render(request, 'error.html', {
		'msg' : error_message_switch(request,503) }),
    }.get(x, render(request, 'error.html', {
		'msg' : error_message_switch(x) } ) )


