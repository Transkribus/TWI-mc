#imports of python modules
import json
#import sys
import re
import random
#import os

#Imports of django modules
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import translation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string

from apps.utils.utils import crop, t_metadata, t_log
from apps.utils.decorators import t_login_required
from apps.utils.services import *

#Imports from app (library)
import settings
from apps.navigation import navigation

#from .forms import RegisterForm, IngestMetsUrlForm, MetsFileForm, QuickIngestMetsUrlForm



#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...

def index(request):
    return render(request, 'library/homepage.html' )


#/library/collections
#view that lists available collections for a user
#@profile("collections.prof")
@t_login_required
def collections(request):
    if not t_refresh() : 
        return HttpResponseRedirect(request.build_absolute_uri(settings.SERVERBASE+"/logout/?next={!s}".format(request.get_full_path())))


    collections = t_collections(request)
    if isinstance(collections,HttpResponse):
        return collections
    return render(request, 'library/collections.html', {'collections': collections} )

#/library/collections
#view that lists available collections for a user
#@profile("collections.prof")
@t_login_required
def collectionsTest(request):
    collections = t_collections(request)

    t_log("in server test", logging.WARN)
    if isinstance(collections,HttpResponse):
        return collections

    pagedatas = []

    # take the first document of a collection
    for coll in collections:
        sys.stdout.write("colId : %s \r\n" % (coll['colId']) )
        sys.stdout.flush()
        docs = t_collection(request, {'collId':coll['colId']})
        if not isinstance(docs, HttpResponseRedirect) and len(docs) > 0:
            doc = docs[0]
        else:
            break
        full_doc = t_document(request, str(coll['colId']), doc['docId'], -1)
        pages= full_doc.get('pageList').get('pages')
        #// means that it is an integer division - not float (float is / )
        a = len(pages)//2
        pagedata = full_doc.get('pageList').get('pages')[a]
        pagedatas.append(str(pagedata['thumbUrl']))
        sys.stdout.write("page url : %s \r\n" % str(pagedata['thumbUrl']))
        sys.stdout.flush()

        if isinstance(doc,HttpResponse):
            return doc

    return render(request, 'library/collections.html', {'collections': collections, 'pagedatas': pagedatas} )

#/library/collection/{colId}
#view that
# - lists documents
# - also lists pages for documents
#@profile("collection.prof")
@t_login_required
def collection(request, collId):

    if not t_refresh() : 
        return HttpResponseRedirect(request.build_absolute_uri(settings.SERVERBASE+"/logout/?next={!s}".format(request.get_full_path())))


    #Avoid this sort of nonsense if possible
    collections = t_collections(request,{'end':None,'start':None})
    if isinstance(collections,HttpResponse):
        return collections

    navdata = navigation.get_nav(collections,collId,'colId','colName')
    #if we didn't have a focus before navigation call, we'll have one after
    collection = navdata.get("focus")
    pagedata = {'collection': collection}
    #merge the dictionaries
    combidata = pagedata.copy()
    combidata.update(navdata)

    return render(request, 'library/collection.html', combidata)

    '''
    #this is actually a call to collections/{collId}/list and returns only the document objects for a collection
    docs = t_collection(request,{'collId':collId})
    #probably a redirect if an HttpResponse
    if isinstance(docs,HttpResponse):
        return docs

    collections = t_collections(request)
    #there is currently no transkribus call for collections/{collId} on its own to fetch just data for collection
    # so we'll loop through collections and pick out collection level metadata freom there
    # The same could be achieved using the list of documents (ie pick first doc match collId with member of colList)
    collection = None
    for x in collections:
        if str(x.get("colId")) == str(collId):
            collection = x

    nav = navigation.up_next_prev(request,"collection",collId,collections)

    #collection view goes down two levels (ie documents and then pages)
    # data prepared fro fancytree.js representation
    for doc in docs:
        doc['collId'] = collId
        doc['key'] = doc['docId']
        doc['folder'] = 'true'
        #fetch full document data with no transcripts for pages //TODO avoid REST request in loop?
        fulldoc  = t_document(request, collId, doc['docId'], 0)
        doc['children'] = fulldoc.get('pageList').get("pages")
        a = len(doc['children']) // 2
        doc['imgurl2show'] = doc['children'][a]['thumbUrl']
        t_log("IMAGEURL2SHOW : %s" % doc['imgurl2show'], logging.WARN)
        #sys.stdout.write("page url : %s \r\n" % doc['imgurl2show'])
        #sys.stdout.flush()
        # for x in doc['children']:
        #   x['title']=x['imgFileName']
        #   x['collId']=collId

    paginator = Paginator(docs, 10)  # Show 5 docs per page
    page = request.GET.get('page')
    try:
        doclist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        doclist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        doclist = paginator.page(paginator.num_pages)

    return render(request, 'library/collection.html', {
        'collId': collId,
        'collection': collection,
        'documents': docs,
#        'documents_json': json.dumps(docs),
        'nav_up': nav['up'],
        'nav_next': nav['next'],
        'nav_prev': nav['prev'],
        'doclist': doclist,
        })
    '''


#/library/document/{colId}/{docId}
# view that lists pages in doc and some doc level metadata
#@profile("document.prof")
@t_login_required
def document(request, collId, docId, page=None):

    if not t_refresh() : 
        return HttpResponseRedirect(request.build_absolute_uri(settings.SERVERBASE+"/logout/?next={!s}".format(request.get_full_path())))


    collection = t_collection(request, {'collId': collId})
    if isinstance(collection,HttpResponse):
        return collection
    fulldoc = t_document(request, collId, docId,-1)
    if isinstance(fulldoc,HttpResponse):
        return fulldoc

    
    nav = navigation.up_next_prev(request,"document",docId,collection,[collId])
    
    navdata = navigation.get_nav(collection,docId,'docId','title')
    #if we didn't have a focus before navigation call, we'll have one after
    #document = navdata.get("focus")
    pagedata = {'document':  fulldoc}
    #merge the dictionaries
    combidata = pagedata.copy()
    combidata.update(navdata)

    '''
    #new for fetching all text regions and text of all pages
    #
    #This performs terribly... Suggest paged ajax calls as with thumbs
    #
    textpages =[]
    textregions = []
    for x in full_doc.get('pageList').get('pages'):
        current_transcript = t_current_transcript(request, collId, docId, x.get("pageNr"))
        t_log("CURRENT_TRANS: %s" % current_transcript,logging.WARN)
        transcript = t_transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))
        regions=transcript.get("PcGts").get("Page").get("TextRegion");

        if isinstance(regions, dict):
            regions = [regions]

        strings = []
        lineList = []
        if regions:
            sys.stdout.write("number of regions on this page : %s \r\n" % len(regions))
            sys.stdout.flush()
            for y in regions:
                lines = y.get("TextLine")
                #region_width = crop(x.get("Coords").get("@points"), 1).get('w')
                if lines:
                    if isinstance(lines, dict):
                        #lines['regionWidth'] = region_width
                        lineList.extend([lines])
                    else: # Assume that lines is a list of lines
                        if lines is not None:
                            for line in lines:
                                #line['regionWidth'] = region_width
                                lineList.extend([line])

                if lineList:
                    sys.stdout.write("number of lines in this region : %s \r\n" % len(lineList))
                    sys.stdout.flush()
                    for z in lineList:
                        if z.get('TextEquiv') is not None:
                            unicode_string = z.get('TextEquiv').get('Unicode')
                        else:
                            unicode_string = "";
                                
                        strings.append(unicode_string)
            
                sys.stdout.write("append strings")
                sys.stdout.flush()
                textregions.append(strings)
                strings=[]
                lineList=[]
        
        textpages.append(textregions)
        textregions=[]
    #new stuff end
    '''
    #merge the dictionaries
    combidata = pagedata.copy()
    combidata.update(navdata)
    
    return render(request, 'library/document.html', combidata)
    '''
    return render(request, 'library/document.html', {
        'metadata': full_doc.get('md'),
        'pageList': full_doc.get('pageList'),
        'textpages': textpages,
        'collId': int(collId),
        'nav_up': nav['up'],
        'nav_next': nav['next'],
        'nav_prev': nav['prev'],
        })
    '''

@t_login_required
def document_page(request, collId, docId, page=None):
    
    if not t_refresh() : 
        return HttpResponseRedirect(request.build_absolute_uri(settings.SERVERBASE+"/logout/?next={!s}".format(request.get_full_path())))
    
    collection = t_collection(request, {'collId': collId})
    if isinstance(collection,HttpResponse):
        return collection
    full_doc = t_document(request, collId, docId,-1)
    if isinstance(full_doc,HttpResponse):
        return full_doc
    
    if (page is None):
        page = 1
    
    index = int(page)-1
    #extract page data from full_doc (may be better from a  separate page data request)
    pagedata = full_doc.get('pageList').get('pages')[index]
#     transcripts = pagedata.get('tsList').get('transcripts')

    sys.stdout.write((str(request)))
    sys.stdout.write((str(request)).rsplit('/', 1)[0])
    sys.stdout.flush()
    startStr = (str(request)).rsplit('/', 1)[0]
    #nav = navigation.up_next_prev(startStr,"document",docId,collection,[collId])
    
    navdata = navigation.get_nav(collection,collId,'docId','title')
#     
#     sys.stdout.write("pagedata url : %s \r\n" % pagedata["url"])
#     sys.stdout.flush()
      
    #new for fetching all text regions and text of all pages
    textlines = []
    current_transcript = t_current_transcript(request, collId, docId, page)
    transcript = t_transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
     
    if isinstance(regions, dict):
        regions = [regions]
#         
# 
    lineList = []
    if regions:
        sys.stdout.write("number of regions on this page : %s \r\n" % len(regions))
        sys.stdout.flush()
        for y in regions:
            if y is not None:
                lines = y.get("TextLine")
                #region_width = crop(x.get("Coords").get("@points"), 1).get('w')
                if lines:
                    if isinstance(lines, dict):
                        #lines['regionWidth'] = region_width
                        lineList.extend([lines])
                    else: # Assume that lines is a list of lines
                        if lines is not None:
                            for line in lines:
                                #line['regionWidth'] = region_width
                                lineList.extend([line])
      
    if lineList:
        for line in lineList:
            if line.get('TextEquiv') is not None:
                unicode_string = line.get('TextEquiv').get('Unicode')
            else:
                unicode_string = "";
            line['Unicode'] = unicode_string
            line_crop = crop(line.get("Coords").get("@points"))#,True)
            line['crop'] = line_crop
            line_id = line.get("@id")
            line['id'] = line_id
    
#     paginator = Paginator(full_doc.get('pageList').get('pages'), 10)  # Show 5 docs per page
#     page = request.GET.get('page')
#     try:
#         doclist = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         doclist = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         doclist = paginator.page(paginator.num_pages)

    return render(request, 'library/document_page.html', {
        'metadata': full_doc.get('md'),
        'textlines': lineList,
        'pageList': full_doc.get('pageList'),
        'collId': int(collId),
        'docId': int(docId),
        'pageNr': page,
        'pagedata': pagedata
#         'nav_up': nav['up'],
#         'nav_next': nav['next'],
#         'nav_prev': nav['prev'],
        })
    
    
    
#/library/document/{colId}/{docId}/{page}
# view that lists transcripts in doc and some page level metadata
#@profile("page.prof")
@t_login_required
def page(request, collId, docId, page):
    #call t_document with noOfTranscript=-1 which will return no transcript data
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc
    # big wodge of data from full doc includes data for each page and for each page, each transcript...
    index = int(page)-1
    #extract page data from full_doc (may be better from a  separate page data request)
    pagedata = full_doc.get('pageList').get('pages')[index]
    transcripts = pagedata.get('tsList').get('transcripts')

#    sys.stdout.write("############## PAGEDATA: %s\r\n" % ( pagedata ) )

    # the way xmltodict parses multiple instances of tags means that if there is one <transcripts> we get a dict,
    # if there is > 1 we get a list. Solution: put dict in list if dict (or get json from transkribus which is
    # parsed better, but not yet available)
    if isinstance(transcripts, dict):
        transcripts = [transcripts]

#    sys.stdout.write("############## PAGEDATA.TRANSCRIPTS: %s\r\n" % ( transcripts ) )

    nav = navigation.up_next_prev(request,"page",page,full_doc.get("pageList").get("pages"),[collId,docId])

    return render(request, 'library/page.html', {
        'pagedata': pagedata,
        'transcripts': transcripts,
        'nav_up': nav['up'],
        'nav_next': nav['next'],
        'nav_prev': nav['prev'],
        'collId': collId,
        'docId': docId,
        })

#/library/transcript/{colId}/{docId}/{page}/{tsId}
# view that lists regions in transcript and some transcript level metadata
@t_login_required
def transcript(request, collId, docId, page, transcriptId):
    #t_page returns an array of the transcripts for a page
    pagedata = t_page(request, collId, docId, page)
    if isinstance(pagedata,HttpResponse):
        return pagedata

    nav = navigation.up_next_prev(request,"transcript",transcriptId,pagedata,[collId,docId,page])

    pageXML_url = None;
    for x in pagedata:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break
    sys.stdout.write("PAGEXML URL : %s \r\n" % (pageXML_url) )
    sys.stdout.flush()

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript


    regions=transcript.get("PcGts").get("Page").get("TextRegion");

    if isinstance(regions, dict):
        regions = [regions]

    if regions:
        for x in regions:
            sys.stdout.write("CUSTOM : %s \r\n" % (x.get("@custom")) )
            sys.stdout.flush()
            x['md'] = t_metadata(x.get("@custom"))

    return render(request, 'library/transcript.html', {
                'transcript' : transcript,
                'regions' : regions,
                'nav_up': nav['up'],
                'nav_next': nav['next'],
                'nav_prev': nav['prev'],
                'collId': collId,
                'docId': docId,
                'pageId': page, #NB actually the number for now
                })

#/library/transcript/{colId}/{docId}/{page}/{tsId}/{regionId}
# view that lists lines in region and some region level metadata
@t_login_required
def region(request, collId, docId, page, transcriptId, regionId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    transcripts = t_page(request,collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return transcripts

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc

    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    t_log("############# TRANSCRIPTS: %s" % transcripts )

    #we are only using the transcripts to get the pageXML for a particular transcript...
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            t_log("############# transcript id comp: %s" % x.get("tsId") )
            t_log("############# transcript id comp: %s" % transcriptId )
            pageXML_url = x.get("url")
            break

    t_log("############# PAGEXML_url: %s" % pageXML_url )

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript

    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        x['key'] = x.get("@id")
        if(str(regionId) == str(x.get("@id"))):
            region = x

    if(region.get("Coords")):
        region['crop'] = crop(region.get("Coords").get("@points"),True)

    nav = navigation.up_next_prev(request,"region",regionId,regions,[collId,docId,page,transcriptId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    lines = region.get("TextLine")
    if isinstance(lines, dict):
        lines = [lines]
    #parse metadata
    if lines:
        for x in lines:
            x['md'] = t_metadata(x.get("@custom"))

    return render(request, 'library/region.html', {
                'region' : region,
                'lines' : lines,
                'nav_up': nav['up'],
                'nav_next': nav['next'],
                'nav_prev': nav['prev'],
                'collId': collId,
                'docId': docId,
                'pageId': page, #NB actually the number for now
                'transcriptId': transcriptId,
                'imageUrl' : pagedata.get("url"),
                })


#/library/transcript/{colId}/{docId}/{page}/{tsId}/{regionId}/{lineId}
# view that lists words in line and some line level metadata
@t_login_required
def line(request, collId, docId, page, transcriptId, regionId, lineId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would
    # rather use transciptId to target a particular transcript
    transcripts = t_page(request,collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return transcripts
    #we are only using the transcripts to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc

    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        if(str(regionId) == str(x.get("@id"))):
            region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
        lines = [lines]


    for x in lines:
        x['key'] = x.get("@id")
        if(str(lineId) == str(x.get("@id"))):
            line = x

    if(line.get("Coords")):
        line['crop'] = crop(line.get("Coords").get("@points"),True)


    nav = navigation.up_next_prev(request,"line",lineId,lines,[collId,docId,page,transcriptId,regionId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]
    #parse metadata
    if words:
        for x in words:
            x['md'] = t_metadata(x.get("@custom"))

    return render(request, 'library/line.html', {
                'line' : line,
                'words' : words,
                'nav_up': nav['up'],
                'nav_next': nav['next'],
                'nav_prev': nav['prev'],
                'collId': collId,
                'docId': docId,
                'pageId': page, #NB actually the number for now
                'transcriptId': transcriptId,
                'regionId': regionId,
                'lineId': lineId,
                'imageUrl' : pagedata.get("url"),
                })

#/library/transcript/{colId}/{docId}/{page}/{tsId}/{regionId}/{lineId}/{wordId}
# view that shows some word level metadata
@t_login_required
def word(request, collId, docId, page, transcriptId, regionId, lineId, wordId):
    # booo hiss
    transcripts = t_page(request, collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return transcripts
    #we are only using the pagedata to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc

    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        if(str(regionId) == str(x.get("@id"))):
            region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
        lines = [lines]

    for x in lines:
        if(str(lineId) == str(x.get("@id"))):
            line = x

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]


    #parse metadata
    for x in words:
        x['key'] = x.get("@id")
        if(str(wordId) == str(x.get("@id"))):
            x['md'] = t_metadata(x.get("@custom"))
            word = x

    if(word.get("Coords")):
        word['crop'] = crop(word.get("Coords").get("@points"),True)

    nav = navigation.up_next_prev(request,"word",wordId,words,[collId,docId,page,transcriptId,regionId,lineId])

    return render(request, 'library/word.html', {
                'word' : word,
                'nav_up': nav['up'],
                'nav_next': nav['next'],
                'nav_prev': nav['prev'],
                'collId': collId,
                'docId': docId,
                'pageId': page, #NB actually the number for now
                'transcriptId': transcriptId,
                'regionId': regionId,
                'lineId': lineId,
                'imageUrl' : pagedata.get("url"),
                })

# Randomly fetch region/line/word this gives us an awful lot of empty responses
# Ideally we want to filter out the transcripts that don't contain good qulity data
# This may be as simple as isPublished(), rather than any analysis on the content
@t_login_required
def rand(request, collId, element):
    collection = t_collection(request, {'collId': collId})

    if isinstance(collection,HttpResponse):
        return collection

    doc = random.choice(collection)

    collection = None
    for x in doc.get("collectionList").get("colList"):
        if str(x.get("colId")) == str(collId):
            collection = x

    pages  = t_document(request, collId, doc.get("docId"), 0)
    if isinstance(pages,HttpResponse):
        return pages
    page = random.choice(pages.get("pageList").get("pages"))

    sys.stdout.write("RANDOM PAGE: %s\r\n" % (page.get("pageNr")) )
    sys.stdout.flush()

    #best to avoid a random transcript, so we'll go for the current in the hope that it is best....
    current_transcript = t_current_transcript(request, collId, doc.get("docId"), page.get("pageNr"))
    transcript = t_transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))

    word = None
    line = None
    region = None

    regions = transcript.get("PcGts").get("Page").get("TextRegion")
    if isinstance(regions, dict):
        regions = [regions]

    if regions:
        region = random.choice(regions)
        if element == "region" :
            sys.stdout.write("region I have\r\n" )
        lines = region.get("TextLine")
    else:
        if transcript.get("PcGts").get("Page").get("TextLine"):
            # I don't think we ever get here.. need to check with UIBK if Page > TextLine is even possible
            sys.stdout.write("I HAVE A LINE DIRECT IN PAGE\r\n" )
            sys.stdout.flush()
            lines = transcript.get("PcGts").get("Page").get("TextLine")
        else:
            sys.stdout.write("NO TEXT IN REGION\r\n" )
            return render(request, 'library/random.html', {
                        "level": element,
                        "text": {},
                        "collection" : collection,
                        "document" : doc,
                        "page" : page,
                        "transcript" : transcript,
                        } )

    if isinstance(lines, dict):
        lines = [lines]

    if element in ['line', 'word'] :
        if lines:
            line = random.choice(lines);
        else:
            return render(request, 'library/random.html', {
                            "level": element,
                            "text": {},
                            "collection" : collection,
                            "document" : doc,
                            "page" : page,
                            "transcript" : transcript,
                            } )

        sys.stdout.write("LINE: %s\r\n" % ( line ) )
        if element == "word" :
            words = line.get("Word")
            if isinstance(words, dict):
                words = [words]

            if words:
                word = random.choice(words);
            else:
                return render(request, 'library/random.html', {
                                "level": element,
                                "text": {},
                                "collection" : collection,
                                "document" : doc,
                                "page" : page,
                                "transcript" : transcript,
                                } )

    switcher = {
        "region" : display_random(request,element,region,collection,doc,page),
        "line" : display_random(request,element,line,collection,doc,page),
        "word" : display_random(request,element,word,collection,doc,page),
    }

    return switcher.get(element, {})

def display_random(request,level,data, collection, doc, page):
    text = None
    if not data :
        text = {}
    elif data.get("TextEquiv"):
        if data.get("TextEquiv").get("Unicode"):
            text = str(data.get("TextEquiv").get("Unicode"))

    return render(request, 'library/random.html', {
                "level": level,
                "text": text,
                "collection" : collection,
                "document" : doc,
                "page" : page,
        } )

@t_login_required
def search(request):
    return render(request, 'library/search.html')

def about(request):
    return render(request, 'library/about.html')

def message_modal(request):
    return render(request, 'library/message_modal.html')

def user_guide(request):
    return render(request, 'library/user_guide.html')

@t_login_required
def users(request, collId, userId):
    return render(request, 'library/users.html')

@t_login_required
def profile(request):
    collections = t_collections(request)
    return render(request, 'library/profile.html', {'collections': collections})

#error pages (where not handled by modals
def collection_noaccess(request, collId):
    if(request.get_full_path() == request.META.get("HTTP_REFERER") or re.match(r'^.*login.*', request.META.get("HTTP_REFERER"))):
        back = None
    else:
        back = request.META.get("HTTP_REFERER") #request.GET.get("back")

    return render(request, 'library/error.html', {
                'msg' : _("I'm afraid you are not allowed to access this collection"),
                'back' : back,
            })
def error(request):
    back = request.build_absolute_uri('/register')

    return render(request, 'library/error.html', {
                'msg' : messages,
                'back' : back,
            })


