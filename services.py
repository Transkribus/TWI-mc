import requests
#workaround for insecure platform warnings...
#http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
#TODO sudo pip install 'requests[security]'
#Possibly check for openssl-devel python-devel libffi-devel (yum)

import xmltodict
from django.http import HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import sys #remove after switching to t_log
from .utils import t_log, t_gen_request_id
import logging # only for log levels (ie logging.WARN etc, which is a maybe crap)
import json
import re


###############################################################
# Helper functions to do request and data handling grunt work
###############################################################

class TranskribusSession(object):

    def __init__(self):
        self.s = requests.Session()

    #set default headers for requests
    def set_default_headers(self,headers):

        if 'clientId' not in headers:
            headers['clientId'] = str(2)
        if 'content-type' not in headers:
            headers['content-type'] = 'application/json'

        return headers

    #Check session cache in case we don't need to bother the transkribus REST service at all
    def check_cache(self,request,t_id, url, params=None) :

        #If our request doesn't have a session we are probably being called from a script. So no cache
        if not hasattr(request,"session") : return None

        # t_id and url as identifer for cached data, Store with key "cache_url" and in first element if data is a list
        # exempting actions data from caching this data will be updated in transkribus by us by virtue of loggin in and viewing stuff.
        # TODO (but not here) - clear cache for certain t_ids that TWI changes... eg on save (or other any triggers that update transkribus data)
        if t_id in request.session and t_id is not "actions":
            request_id = t_gen_request_id(url,params,request.user.tsdata.userId if hasattr(request.user,'tsdata') else 1)
#            if t_id is "collections" : t_log("request_id:userid %s:%s" % (request_id,request.user.tsdata.userId), logging.WARN)
    #        t_log("CHECK FOR CACHE of %s (%s) WITH: %s " % (t_id, request.user.tsdata.userId, request_id), logging.WARN)
            if request_id in request.session[t_id] :
    #            t_log("USING CACHE: %s " % request_id, logging.WARN)
                return request.session[t_id][request_id]

        #no data cached for this t_id/url pair, return None
        return None

    #Set the session cache after a successful request to transkribus REST service
    def set_cache_value(self, request,t_id,data,url,params=None) :

        #If our request doesn't have a session we are probably being called from a script. So no cache
        if not hasattr(request,"session") : return None

        #Use the t_id as identifer for cached data, Store the url with key "cache_url" (in first element if data is a list)
        request_id = t_gen_request_id(url,params,request.user.tsdata.userId if hasattr(request.user,'tsdata') else 1)

    #    t_log("CACHING %s for %s with request_id : %s" % (t_id, request.user.tsdata.userId,request_id), logging.WARN )
        if t_id not in request.session : request.session[t_id] = {}
        request.session[t_id][request_id] = data

    #Make a request for data (possibly) to the transkribus REST service make
    #use of helper functions and calling the appropriate data handler when done
    def request(self,request,t_id,url,params=None,method=None,headers=None,handler_params=None,ignore_cache=None,data=None):
        #t_log("IN REQUEST t_id: %s  ignore cache: %s" % (t_id,ignore_cache),logging.WARN)
        #Check for cached value and return that
        if ignore_cache is None :
            cache_data = self.check_cache(request, t_id, url, params)
            if cache_data :
                return cache_data

        #Add default headers to *possibly* already defined header data
        if not headers : headers = {}
        headers = self.set_default_headers(headers)

        #Default method is GET
        try:
            if method == 'POST' :
                r = self.s.post(url, params=params, verify=False, headers=headers, data=data)
            else:
                r = self.s.get(url, params=params, verify=False, headers=headers)
        except requests.exceptions.ConnectionError as e:
            t_log("COULD NOT CONNECT TO TRANSKRIBUS: %s" % (e), logging.WARN)
            return HttpResponse("Service Unavailable", status=503)

        #t_log("URL : %s PARAMS : %s" % (url,params), logging.WARN)
        #Check responses,
        #	401: unauth
        #	403+rest+collId: forbidden collection
        #	400+register bad data input
        #	raise error for the rest
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code not in (401, 403, 400, 404, 500, 503):
                #raise e.response.status_code
                #exceptions must derive from BaseException
                raise e
            if e.response.status_code == 400 : # and handler_params is not None and "collId" in handler_params):
                if re.match(r'^.*/rest/user/register', url) :
                    #t_register_handler only handles exceptions, if reg is successsful then t_user_data_handlercan be used
                    return t_register_handler(r,handler_params)

            #otherwise you get logged out...
            t_log("TRANSKRIBUS SAYS NO: %s (%s) - request: %s" % (e.response.reason, e.response.status_code, url), logging.WARN)
#            return HttpResponseRedirect(request.build_absolute_uri(settings.SERVERBASE+"/logout/?next={!s}".format(request.get_full_path())))
            return HttpResponse(e.response.reason, status=e.response.status_code)

        # Pass transkribus response to handler (NB naming convention is t_[t_id]_handler(r, handler_params)
        # handler_params are for things that we might need to pass through this t_request to the handler
        data = eval("self."+t_id+"_handler(r,handler_params)")

        #We store the data in the sesison cache
        self.set_cache_value(request,t_id,data,url,params)
        #And return it too
        return data

    ###########################################################################################
    # Request/handler functions
    # 1. Request specific bits of data from transkribus REST service
    #    Set a url and t_id (ref dor data), set any specific headers or paramters, call request
    # 2. Handle the response, do any datamungery before passing back to view
    #    The handler must be named thus in order that t_request can find it: t_[t_id]_handler(r)
    #    Recieves response from t_request, does stuff if necessary, returns data via 1. to view
    #    TODO will probably need to pass through params in some cases to help mung the data
    ###########################################################################################


    def register(self,request):

        url = settings.TRP_URL+'user/register'
        t_id = "user_data" # note we are using the same t_id as for t_login...
        t_log("G_CAPTCH_RESPONSE: %s" % request.POST.get('g-recaptcha-response'))
        params = {'user': request.POST.get('user'),
                    'pw': request.POST.get('pw'),
                    'firstName': request.POST.get('firstName'),
                    'lastName': request.POST.get('lastNaame'),
    #               'email': request.POST.get('email'),
    #               'gender': request.POST.get('gender'),
    #               'orcid':request.POST.get('orcid'),
                    'token': request.POST.get('g-recaptcha-response'),
                    'application': "WEB_UI"}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        return self.request(request,t_id,url,params,"POST",headers)

    # REG FAIL HANDLER
    def register_handler(self,r,params=None):
        t_log("400 from register...")
        raise ValueError('%s' % (r.text))

    def login(self, user, pw):
        url = settings.TRP_URL+'auth/login'
        t_id = "user_data" # note we are using the same t_id as for t_register... This is OK because the data response will be the same... I think
        params = {'user': user, 'pw': pw}
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        r = self.s.post(url, params=params, verify=False, headers=headers)

        if r.status_code != requests.codes.ok:
            return None

        return xmltodict.parse(r.text).get('trpUserLogin')

    # NOT currently used
    def user_data_handler(self,r,params=None):
        return xmltodict.parse(r.text).get('trpUserLogin')

    #refresh transkribus session (called by t_login_required decorator to test persistence/validity of transkribus session)
    ############## DEPRECATED ########################
    def refresh(self):

        url = settings.TRP_URL+'auth/refresh'
        r = self.s.post(url, verify=False)

        t_log("### t_refresh response STATUS_CODE: %s" % (r.status_code) )

        if r.status_code != requests.codes.ok:
            return False
        else:
            return True
    #####################################################
    def invalidate(self):

        url = settings.TRP_URL+'auth/invalidate'
        r = self.s.post(url, verify=False)

        t_log("### t_invalidate response STATUS_CODE: %s" % (r.status_code), logging.WARN )

        if r.status_code != requests.codes.ok:
            return False
        else:
            return True

    #t_actions_info called to get lookup for action types for subsequent action list calls
    def actions_info(self,request):
        #The url for the transkribus rest call
        url = settings.TRP_URL+'actions/info'
        #the id to use call the correct data handler and store the data
        t_id = "action_types"
        #Return the data from the request (via the handler, defined below)
        return self.request(request,t_id,url)
    # Below is the simplest case imaginable
    def action_types_handler(self,r,params=None):
        return json.loads(r.text)

    #t_actions_count #NB this call is not yet available
    def actions_count(self,request,params=None):
        url = settings.TRP_URL+'actions/count'
        t_id = "actions_count"
        return self.request(request,t_id,url,params)

    def actions_count_handler(self,r,params=None):
        return json.loads(r.text)

    #t_actions_list
    def actions(self,request,params=None):
        url = settings.TRP_URL+'actions/list'
        t_id = "actions"
        #We always want fresh data on actions as they are always changing
        t_log("ACTION PARAMS: %s" % params, logging.WARN)
        return self.request(request,t_id,url,params=params,ignore_cache=True)

    def actions_handler(self,r,params=None):
        return json.loads(r.text)

    #t_collection_recent called to get most recently accessed page in a given collection
    def collection_recent(self,request,params) :
        url = settings.TRP_URL+'actions/list'
        t_id = "collection_recent"
        params['typeId'] = 1
        params['nValues'] = 1
        return self.request(request,t_id,url,params,"GET")

    def collection_recent_handler(self,r,params=None):
        t_log("collection_recent: %s " % r.text)
        return json.loads(r.text)

    #t_document_recent called to get most recently accessed page in a given document
    def document_recent(self,request,params):
        url = settings.TRP_URL+'actions/list'
        t_id = "document_recent"
        params['typeId'] = 1
        params['nValues'] = 1
        return self.request(request,t_id,url,params,"GET")

    def document_recent_handler(self,r,params=None):
        t_log("document_recent: %s " % r.text)
        return json.loads(r.text)

    #t_collections_count
    def collections_count(self,request,params=None):
        url = settings.TRP_URL+'collections/count'
        t_id = "collections_count"

        return self.request(request,t_id,url,params)

    def collections_count_handler(self,r,params=None):
        return json.loads(r.text)

    def collections(self,request,params=None,ignore_cache=None):
        url = settings.TRP_URL+'collections/list'
        t_id = "collections"
        return self.request(request,t_id,url,params=params,ignore_cache=ignore_cache)

    def collections_handler(self, r,params=None):
        t_collections = json.loads(r.text)
        t_log(str(t_collections))
        #use common param 'key' for ids (may yet drop...)
        for col in t_collections:
            col['key'] = col['colId']
        return t_collections

    #t_users_count
    def users_count(self,request,params=None):
        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/userlist/count'
        t_id = "users_count"
        return self.request(request,t_id,url,params,"GET",None,{"collId": params.get('collId')})

    def users_count_handler(self,r,params=None):
        return json.loads(r.text)

    #t_users_list
    def users(self,request,params=None):
        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/userlist'
        t_id = "users"

        return self.request(request,t_id,url,params)

    def users_handler(self,r,params=None):
        return json.loads(r.text)

    #t_user (by username... yuk!)
    def user(self,request,params=None):
        url = settings.TRP_URL+'user/findUser'
        t_id = "user"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        t_log("USER url: %s" % url,logging.WARN)
        t_log("USER params: %s" % params,logging.WARN)

        return self.request(request,t_id,url,params,'GET',headers)

    def user_handler(self,r,params=None):
        t_log("USER response: %s" % r.text,logging.WARN)
        return xmltodict.parse(r.text).get('trpUsers').get('trpUser')

    def collection(self,request,params):
        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/list'
        t_id = "collection"
        return self.request(request,t_id,url,params,"GET",None,{"collId": params.get('collId')})

    def collection_handler(self,r,params=None):
        return json.loads(r.text)

    def collection_count(self,request,params):
        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/count'
        t_id = "collection_count"

        return self.request(request,t_id,url,params)

    def collection_count_handler(self,r,params=None):
        return json.loads(r.text)

    def collection_metadata(self,request,params):
        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/metadata'
        params['stats']='true'
        t_id = "collection_metadata"
        return self.request(request,t_id,url,params,"GET",None,{"collId": params.get('collId')})

    def collection_metadata_handler(self,r,params=None):
        return json.loads(r.text)

    #Alias t_documents > t_collection
    def documents(self,request,params):
        return self.collection(request,params)

    def documents_count(self,request,params):
        return self.collection_count(request,params)

    def fulldoc(self,request,params):

        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/'+str(params.get('docId'))+'/fulldoc'
        t_id = "fulldoc"
        return self.request(request,t_id,url,params)

    def fulldoc_handler(self,r,params=None):
        return json.loads(r.text)

    def document(self,request, collId, docId, nrOfTranscripts=None,ignore_cache=None):
        url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/fulldoc'
        t_id = "document"
        params = {}
        if not nrOfTranscripts is None:
            params['nrOfTranscripts'] = nrOfTranscripts
        return self.request(request,t_id,url,ignore_cache=ignore_cache)

    def document_handler(self,r,params=None):
        t_doc = json.loads(r.text)
        pages = t_doc.get("pageList").get("pages")
        for x  in pages:
            x['key'] = x.get('pageNr') #I'm aware this will replacce the legitimate key....

        return t_doc

    #returns a list of transcripts for a page, no page metadata...
    def page(self,request,collId, docId, page):

        #list of transcripts for this page
        url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/list'
        t_id = "page"
        return self.request(request,t_id,url)

    #returns (nr_of_transcribed_lines, nr_of_transcribed_words) for a document
    def docStat(self,request, params):

        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/'+str(params.get('docId'))+'/docStat'
        t_id = "docStat"
        return self.request(request,t_id,url)

    def docStat_handler(self,r,params=None):
        return json.loads(r.text)

    #returns (nr_of_transcribed_lines, nr_of_transcribed_words) for a whole collection
    def collStat(self,request, params):

        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/collStat'
        t_id = "collStat"
        return self.request(request,t_id,url)

    def collStat_handler(self,r,params=None):
        return json.loads(r.text)

    #returns (nr_of_transcribed_lines, nr_of_transcribed_words) for a document
    def countDocTags(self,request, params):

        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/'+str(params.get('docId'))+'/countTags'
        t_id = "countDocTags"
        return self.request(request,t_id,url, params)

    def countDocTags_handler(self,r,params=None):
        return json.loads(r.text)

    def countCollTags(self,request, params):

        url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/countTags'
        t_id = "countCollTags"
        return self.request(request,t_id,url, params)

    def countCollTags_handler(self,r,params=None):
        return json.loads(r.text)

    def page_handler(self,r,params=None):

        t_page = json.loads(r.text)

        #TODO would prefer a pageId rather than "page" which is a the page number
        for x  in t_page:
            #key is used already for transcripts, however using key is handy for jquery things like fancy tree...
            x['key'] = x.get('tsId')

        return self.page

    #returns the current transcript for a page
    def current_transcript(self,request,collId, docId, page):

        #list of transcripts for this page
        url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/curr'
        t_id="current_transcript"
        return self.request(request,t_id,url)

    def current_transcript_handler(self,r,params=None):
        t_transcript = json.loads(r.text)
        t_transcript['key'] = t_transcript.get('tsId')
        return t_transcript

    #I think that current_ts_md_for_page woudl be a better name for this one as it doesn't actually return the transcript....
    def current_ts_md_for_page(self,request,collId, docId, page):
        return self.current_transcript(request,collId, docId, page)

    def transcript(self,request,transcriptId,url):

        t_id = "transcript"
        headers = {'content-type': 'application/xml'}
        params = {}
        return self.request(request,t_id,url,params,"GET",headers,{'transcriptId': transcriptId})

    def transcript_handler(self,r,params=None):
        t_transcript=xmltodict.parse(r.text)
        t_transcript['tsId'] = params.get('transcriptId')
        return t_transcript

    def transcript_xml(self,request,transcriptId,url):
        t_id = "transcript_xml"
        headers = {'content-type': 'application/xml'}
        params = {}
        return self.request(request,t_id,url,params,"GET",headers,{'transcriptId': transcriptId})

    def transcript_xml_handler(self,r,params=None):
        return r.text

    def create_collection_handler(self,r, params=None):
        return r.status_code == requests.codes.ok

    #t_crowdsourcing_count
    def crowdsourcing_count(self,request,params=None):
        url = settings.TRP_URL+'crowdsourcing/count'
        t_id = "crowdsourcing_count"
        return self.request(request,t_id,url,params)

    def crowdsourcing_count_handler(self,r,params=None):
        return json.loads(r.text)

    #t_crowdsourcing_list
    def crowdsourcing(self,request,params=None):
        url = settings.TRP_URL+'crowdsourcing/list'
        t_id = "crowdsourcing"

        return self.request(request,t_id,url,params)

    def crowdsourcing_handler(self,r,params=None):
        return json.loads(r.text)

    #t_crowdsourcing_subscribe
    def crowdsourcing_subscribe(self,request,params):
        url = settings.TRP_URL+'crowdsourcing/'+str(params.get('collId'))+'/subscribe'
        t_id = "crowdsourcing_subscribe"

        params = {'collId': params.get('collId')}
        headers = {'content-type': "application/json"}

        return self.request(request, t_id, url, method='POST',params=params,headers=headers)

    def crowdsourcing_subscribe_handler(self,r,params=None):
        return r.status_code

    #t_crowdsourcing_unsubscribe
    def crowdsourcing_unsubscribe(self,request,params):
        url = settings.TRP_URL+'crowdsourcing/'+str(params.get('collId'))+'/unsubscribe'
        t_id = "crowdsourcing_unsubscribe"

        params = {'collId': params.get('collId')}
        headers = {'content-type': "application/json"}

        return self.request(request, t_id, url, method='POST',params=params,headers=headers)

    def crowdsourcing_unsubscribe_handler(self,r,params=None):
        return r.status_code

    #TODO find out why the save and status calls are not using t.request like everything else
    # Saves transcripts.
    def save_transcript(self, request, transcript_xml, collId, docId, page, parent):
        #added transcript id as parent as per Transkribus/TWI-edit#38
        params = {"status": "IN_PROGRESS", 'parent': parent, 'toolName': 'Web Interface'}
        headers = {"content-type": "application/xml"}

        url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/text'
        t_id = "save_transcript"

        # Remove the old version from cache. NB better to do this after the request
        del request.session['current_transcript']

        return self.request(request, t_id, url, method="POST", params=params, headers=headers,ignore_cache=True, data=transcript_xml)
        #r = self.s.post(url, verify=False, headers=headers, params=params, data=transcript_xml)
#        return None

    def save_transcript_handler(self,r,params=None):
        t_log("RESPONSE: %s " % r, logging.WARN)
        return r.status_code

    def save_page_status(self, request, status, collId, docId, pageNr, transcriptId):
        params = {'status': status}
        headers = {'content-type': 'text/plain'}

        t_id = "save_page_status"

        url = settings.TRP_URL + 'collections/%(collId)s/%(docId)s/%(pageNr)s/%(transcriptId)s' % {
            'collId': collId,
            'docId': docId,
            'pageNr': pageNr,
            'transcriptId': transcriptId
        }

        return self.request(request, t_id, url, method="POST", params=params, headers=headers,ignore_cache=True)

    def save_page_status_handler(self,r,params=None):
        return r.status_code



    def fulltext_search(self, request, params=None) :
        url = settings.TRP_URL+'search/fulltext'
        t_id = "fulltext_search"
        return self.request(request,t_id,url,params=params,ignore_cache=True)

    def fulltext_search_handler(self,r,params=None):
        return json.loads(r.text)


    ####################################
    # TODO decide what to do with this stuff (ie mets up/downloading, create_collection, etc)
    # It was previouly lumped to gether with everything in the old library app
    # Some of these things will be popular with some partners
    # There is a nascent "upload" app that is meant to make use of them
    ##################################

    def download_mets_xml(self,mets_url):
        r = self.s.get(mets_url)
        # TODO Consider returning some "document name" or such to enable the user to verify the document title...?
        return r.text

    def ingest_mets_xml(self,collId, mets_file):

        url = settings.TRP_URL+'collections/' + collId + '/createDocFromMets'
        files = {'mets':  mets_file}
        r = self.s.post(url, files=files, verify=False)

        if r.status_code != requests.codes.ok:
            t_log("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.text) )
            return None
        # TODO What to do when we're successful?'

    def ingest_mets_url(self,collId, mets_url):

        url = settings.TRP_URL+'collections/' + collId + '/createDocFromMetsUrl'
        params = {'fileName': mets_url}#, 'checkForDuplicateTitle': 'false'}# Perhaps this won't work even for testing! TODO Resolve!
        r = self.s.post(url, params=params, verify=False)

        t_log("Ingesting document from METS XML file URL: %s%% \r\n" % (mets_url) )
        if (r.status_code == requests.codes.ok):
            return True
        else:
            t_log("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.text) )
            return None

    def create_collection(self,request, collection_name):
        url = settings.TRP_URL+'collections/createCollection'
        params = {'collName': collection_name}
        headers = {'content-type': None}
        #clear cached collections list so that the new one will appear when created
        request.session['collections'] = None
        t_id = "create_collection"
        #actucally this will need more working on if we decide to keep (need handler etc)
        return self.request(request, t_id, url, method='POST', params=params, headers=headers, ignore_cache=True)

    def jobs(self,status = ''):
        url = settings.TRP_URL+'jobs/list'
        params = {'status': status}
        r = self.s.get(url, params=params, verify=False)
        if r.status_code != requests.codes.ok:
            t_log("Error getting jobs: %s \r\n ERROR: %s" % (r.status_code, r.text))
            return None
        jobs_json=r.text
        jobs = json.loads(jobs_json)
        return jobs

    def job_count(self,status = ''):
        url = settings.TRP_URL+'jobs/count'
        params = {'status': status}
        r = self.s.get(url, params=params, verify=False)
        if r.status_code != requests.codes.ok:
            t_log("Error getting job count: %s \r\n ERROR: %s" % (r.status_code, r.text))
            return None
        count=r.text
        return count

    def kill_job(self,job_id):
        url = settings.TRP_URL + 'jobs/' + job_id + '/kill'
        r = self.s.post(url, verify=False)

        t_log("Response to kill job: %s  \r\n" % (r.status_code) )

        return r.status_code == requests.codes.ok
