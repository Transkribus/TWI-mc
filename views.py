#imports of python modules
#import json
#import sys
#import re
#import random

from django.template.defaultfilters import linebreaksbr

#Imports of django modules
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.shortcuts import render
#from django.utils import translation
#from django.contrib.auth.models import User
#from django.contrib.auth.decorators import login_required
#from django.contrib import messages
#from django.utils.translation import ugettext_lazy as _
#from django.template.loader import render_to_string

#from django.contrib.auth.decorators import login_required #for ajax reponses
from apps.utils.decorators import t_login_required, t_login_required_ajax
from apps.utils.services import *
from apps.utils.utils import t_log

from apps.querystring_parser.querystring_parser import parser

from .forms import RegisterForm

#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...


def register(request):
#TODO this is generic guff need to extend form for extra fields, send reg data to transkribus and authticate (which will handle the user creation)

    if request.user.is_authenticated(): #shouldn't really happen but...
#        return HttpResponseRedirect(request.build_absolute_uri('/library/'))
        return HttpResponseRedirect(request.build_absolute_uri(request.resolver_match.app_name))
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        sys.stdout.write("### IN t_register \r\n" )
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            sys.stdout.write("### IN form is valid \r\n" )

            # user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            try:
                t_register(request)
                return HttpResponseRedirect(request.build_absolute_uri(request.resolver_match.app_name))
                #tried out modal here and it is nice (but not really for registration)
#               messages.info(request, _('Registration requested please check your email.'))
#                return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
            except ValueError as err:
                sys.stdout.write("### t_register response ERROR RAISED: %s  \r\n" % (err) )
#               return render(request, 'registration/register.html', {'register_form': form} )
                #Why the f**k won't this redirect?!? TODO fix or try another method
                return HttpResponseRedirect(request.build_absolute_uri('/library/error'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    #Recpatch errors are not properly dislpayed by bootstrap-form... hmph
    return render(request, 'registration/register.html', {'register_form': form} )

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
    t_log("TABLE_AJAX for %s" % list_name, logging.WARN)

    (data,count) = paged_data(request,t_list_name,params)
    
    if list_name == 'actions' :
        t_log("ACTION DATA: %s" % data, logging.WARN)

    #we want to add statistical data to the title column like nr_of_transcribed_lines, nr_of_transkribed_words, tags....
#===============================================================================
#     if list_name == 'documents':
#         for element in data:
#             #docStat = t_docStat(request,{'collId': collId, 'docId': int(element.get('docId'))})
#             docId = element.get('docId')  
#             params2 = {'collId': collId, 'docId': docId}
#             personParam = {'collId': collId, 'docId': docId, 'tagName': 'person'}
#             placeParam = {'collId': collId, 'docId': docId, 'tagName': 'place'}
#             dateParam = {'collId': collId, 'docId': docId, 'tagName': 'date'}
#             abbrevParam = {'collId': collId, 'docId': docId, 'tagName': 'abbrev'}
#             otherParam = {'collId': collId, 'docId': docId, 'tagName': 'other'}
#             personCount = eval("t_countDocTags(request,personParam)")
#             placeCount = eval("t_countDocTags(request,placeParam)")
#             dateCount = eval("t_countDocTags(request,dateParam)")
#             abbrevCount = eval("t_countDocTags(request,abbrevParam)")
#             otherCount = eval("t_countDocTags(request,otherParam)")
# #             print('nr of person tags: ' + str(personCount))
# #             print('place tags' + str(placeCount))
# #             print('date tags' + str(dateCount))
# #             print('abbrev tags' + str(abbrevCount))
# #             print('other tags' + str(otherCount))
#             
#             tagsString = getTagsString(personCount, placeCount, dateCount, abbrevCount, otherCount)
#             
#             docStat = eval("t_docStat(request, params2)")
#             #print(docStat)
#             #TODO call rest service to get the stats
#             if 'nr_lines_transcribed' not in str(element.get('title')):
#                 element.update({'title': str(element.get('title'))+'<br/>nr_lines_transcribed: '+ str(docStat.get('nrOfTranscribedLines')) + '<br/>nr_words_transcribed: ' + str(docStat.get('nrOfWords'))}) 
#                 
#             if tagsString and 'Tags' not in str(element.get('title')):
#                 element.update({'title': str(element.get('title'))+tagsString}) 
#===============================================================================
    
    #print(data)
    
    #===========================================================================
    # if list_name == 'collections':
    #     for element in data:
    #         collId = element.get('colId') 
    #         params3 = {'collId': collId}
    #           
    #         personParam = {'collId': collId, 'tagName': 'person'}
    #         placeParam = {'collId': collId, 'tagName': 'place'}
    #         dateParam = {'collId': collId, 'tagName': 'date'}
    #         abbrevParam = {'collId': collId, 'tagName': 'abbrev'}
    #         otherParam = {'collId': collId, 'tagName': 'other'}
    #         personCount = eval("t_countCollTags(request,personParam)")
    #         placeCount = eval("t_countCollTags(request,placeParam)")
    #         dateCount = eval("t_countCollTags(request,dateParam)")
    #         abbrevCount = eval("t_countCollTags(request,abbrevParam)")
    #         otherCount = eval("t_countCollTags(request,otherParam)")
    #           
    #         tagsString = getTagsString(personCount, placeCount, dateCount, abbrevCount, otherCount)
    #               
    #         print(tagsString)
    #       
    #         collStat = eval("t_collStat(request, params3)")
    #           
    #         if 'nr_lines_transcribed' not in str(element.get('colName')):
    #             element.update({'colName': str(element.get('colName'))+'<br/>nr_lines_transcribed: '+ str(collStat.get('nrOfTranscribedLines')) + '<br/>nr_words_transcribed: ' + str(collStat.get('nrOfWords'))}) 
    #               
    #         if tagsString and 'Tags' not in str(element.get('colName')):
    #             element.update({'colName': str(element.get('colName'))+tagsString}) 
    #===========================================================================

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(data,HttpResponse):
        t_log("data request has failed... %s" % data)
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)

    filters = {
                'actions' : ['time', 'colId', 'colName', 'docId', 'docName', 'pageId', 'pageNr', 'userName', 'type'],
                'collections' : ['colId', 'colName', 'description', 'role'],
                'users' : ['userId', 'userName', 'firstname', 'lastname','email','affiliation','created','role'], #NB roles in userCollection
                'documents' : ['docId','title', 'desc', 'author','uploadTimestamp','uploader','nrOfPages','language','status'],
#               'pages' : ['pageId','pageNr','thumbUrl','status', 'nrOfTranscripts'], #tables
                'pages' : ['pageId','pageNr','imgFileName','thumbUrl','status'], #thumbnails
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

    documents = t_documents(request,{'collId': collId})
    if isinstance(documents,HttpResponse):
        return documents
    #grab first doc
    docId = next(iter(documents or []), None).get("docId")

    fulldoc = t_fulldoc(request,{'collId': collId, 'docId': docId})
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
    
    fulldoc = t_document(request, collId, docId,-1)
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
def page_img(request, collId, docId, page):
    import timeit
    
    fulldoc = t_document(request, collId, docId, page)
    if isinstance(fulldoc,HttpResponse):
        return fulldoc
    
    currPage = fulldoc.get('pageList').get("pages")[page]
#    a = len(pages) // 2 #page from the middle?
    #maybe just grab first page?
    img_url = currPage['url']

    return JsonResponse({
            'url': img_url
        },safe=False)

##########
# Helpers
##########

# paged_data:
#       - Handle common parameters for paging and filtering data
#       - Calls utils.services.t_[list_name] requests
#       - Some params must be passed in params (eg ids from url, typeId from calling function)
#       - Some params are set directly from REQUEST, but can be overridden by params (eg nValues)

@t_login_required_ajax
def paged_data(request,list_name,params=None):#collId=None,docId=None):

    #collect params from request into dict
    dt_params = parser.parse(request.GET.urlencode())

    print('the xx request ' + str(request))
#    t_log("DT PARAMS: %s" % dt_params)
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
        #params['nValues'] = int(dt_params.get('length')) if dt_params.get('length') else settings.PAGE_SIZE_DEFAULT
        #this means we fetch all data from rest service and show in  a paged datatable - length is shown after data has loaded
        params['nValues'] = int(dt_params.get('length')) if dt_params.get('length') else 0

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
    t_log("SENT PARAMS: %s" % params)
    data = eval("t_"+list_name+"(request,params)")

    #Get count
    count=None
    #When we call a full doc we *probably* want to count the pages (we can't fo that with a /count call)
    if list_name not in ["fulldoc"]:
        count = eval("t_"+list_name+"_count(request,params)")
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
            filtered_datum[field] = datum.get(field) if datum.get(field) else "n/a" #TODO this will n/a 0!!
        filtered.append(filtered_datum)

    return filtered
