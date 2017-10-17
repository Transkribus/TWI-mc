#imports of python modules
import json
#import sys
import re
import random
#import os
import sys

#Imports of django modules
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import translation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from apps.utils.decorators import t_login_required_ajax
from apps.utils.utils import crop, t_metadata, t_log
from apps.utils.services import *
from apps.utils.views import *


#Imports from app (library)
import settings
import apps.library.settings
from apps.navigation import navigation

import apps.library.settings

#from .forms import RegisterForm, IngestMetsUrlForm, MetsFileForm, QuickIngestMetsUrlForm

def index(request):
    return render(request, 'library/homepage.html' )


#/library
#view that lists available collections for a user
@login_required
def collections(request):
    t = request.user.tsdata.t

    collections = t.collections(request,{'empty':'true'})
    if isinstance(collections,HttpResponse):
        return apps.utils.views.error_view(request,collections)
    return render(request, 'library/collections.html', {'collections': collections} )

#/library/{colId}
#view that
# - lists documents
# - also lists pages for documents
@login_required
def collection(request, collId):
    t = request.user.tsdata.t

    #Avoid this sort of nonsense if possible
    collections = t.collections(request,{'end':None,'start':None,'empty':'true'})
    if isinstance(collections,HttpResponse):
        return apps.utils.views.error_view(request,collections)

    navdata = navigation.get_nav(collections,collId,'colId','colName')
    #if we didn't have a focus before navigation call, we'll have one after
    collection = navdata.get("focus")
    
    collIdParam = {'collId': collId}

    personParam = {'collId': collId, 'tagName': 'person'}
    placeParam = {'collId': collId, 'tagName': 'place'}
    dateParam = {'collId': collId, 'tagName': 'date'}
    abbrevParam = {'collId': collId, 'tagName': 'abbrev'}
    otherParam = {'collId': collId, 'tagName': 'other'}
    personCount = t.countCollTags(request,personParam)
    if isinstance(personCount,HttpResponse):
        return apps.utils.views.error_view(request,personCount)
    placeCount = t.countCollTags(request,placeParam)
    if isinstance(placeCount,HttpResponse):
        return apps.utils.views.error_view(request,placeCount)
    dateCount = t.countCollTags(request,dateParam)
    if isinstance(dateCount,HttpResponse):
        return apps.utils.views.error_view(request,dateCount)
    abbrevCount = t.countCollTags(request,abbrevParam)
    if isinstance(abbrevCount,HttpResponse):
        return apps.utils.views.error_view(request,abbrevCount)
    otherCount = t.countCollTags(request,otherParam)
    if isinstance(otherCount,HttpResponse):
        return apps.utils.views.error_view(request,otherCount)

    tagsString = getTagsString(personCount, placeCount, dateCount, abbrevCount, otherCount)

    print(tagsString)

    collStat = t.collStat(request, collIdParam)
    if isinstance(collStat,HttpResponse):
        return apps.utils.views.error_view(request,collStat)

    if (collection):
        print("print collection: " + str(collection))
        collection['collStat'] = '%i words' % collStat.get('nrOfWords')
        collection['tagsString'] = tagsString

    print("print navdata: "+str(navdata))
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


#/library/{colId}/{docId}
# view that lists pages in doc and some doc level metadata
@login_required
def document(request, collId, docId, page=None):
    t = request.user.tsdata.t

    collection = t.collection(request, {'collId': collId})
    if isinstance(collection,HttpResponse):
        return apps.utils.views.error_view(request,collection)
    fulldoc = t.document(request, collId, docId,-1)
    if isinstance(fulldoc,HttpResponse):
        return apps.utils.views.error_view(request,fulldoc)

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

def _get_collection(document, collId):
    for collection in document['collectionList']['colList']:
        if int(collection['colId']) == int(collId):
            return collection


def collection_statistics(request, collId):
    t = request.user.tsdata.t
    collections = t.collection(request, {'collId': collId})
    if isinstance(collections,HttpResponse):
        return apps.utils.views.error_view(request,collections)

    collection = _get_collection(collections[0], collId)

    title_desc = ''
    title_desc += '<p><b>%s</b> (%s)</p>' % (collection['colName'], collId)
    if 'description' in collection:
        title_desc += '<p id="long_text_%s">%s</p>' % (collId, collection['description'])

    #Add collection of data on last saved page (aka recent)
    recent = t.collection_recent(request,collId)
    if isinstance(recent,HttpResponse):
        return apps.utils.views.error_view(request,recent)

    if recent : 
        #recent will be a single item array
        recent = recent[0]
        if 'pageNr' in recent:
            title_desc += str(_('Go to <a href="%s">last saved page</a> in this collection')) % reverse('edit:correct', args=[collId,recent.get('docId'),recent.get('pageNr')])


    return JsonResponse({'titleDesc': title_desc}, safe=False)


#Fetch a single thumb url from the document referenced
def document_statistics(request, collId, docId):
    import timeit

    t = request.user.tsdata.t

    idParam = {'collId': collId, 'docId': docId}
    personParam = {'collId': collId, 'docId': docId, 'tagName': 'person'}
    placeParam = {'collId': collId, 'docId': docId, 'tagName': 'place'}
    dateParam = {'collId': collId, 'docId': docId, 'tagName': 'date'}
    abbrevParam = {'collId': collId, 'docId': docId, 'tagName': 'abbrev'}
    otherParam = {'collId': collId, 'docId': docId, 'tagName': 'other'}
    personCount = t.countDocTags(request,personParam)
    placeCount = t.countDocTags(request,placeParam)
    dateCount = t.countDocTags(request,dateParam)
    abbrevCount = t.countDocTags(request,abbrevParam)
    otherCount = t.countDocTags(request,otherParam)

    tagsString = getTagsString(personCount, placeCount, dateCount, abbrevCount, otherCount)

    docStat = t.docStat(request, idParam)
    docStatString = '%i lines, %i words' % (docStat.get('nrOfTranscribedLines'), docStat.get('nrOfWords'))
    view_links = '<ul class="list-group list-unstyled text-center twi-view-link-list">'
    view_links += '<li class="list-group-item"><a href="%s?i=i">Image</a></li>' % reverse('edit:correct', args=[collId, docId, 1])
    view_links += '<li class="list-group-item"><a href="%s?i=lbl">Line by line</a></li>' % reverse('edit:correct', args=[collId, docId, 1])
    view_links += '<li class="list-group-item"><a href="%s?i=sbs">Side by side</a></li>' % reverse('edit:correct', args=[collId, docId, 1])
    view_links += '<li class="list-group-item"><a href="%s?i=t">Text</a></li>' % reverse('edit:correct', args=[collId, docId, 1])
    view_links += '</ul>'

#    view_links = '<div class="btn-group-vertical" role="group">'
#    view_links += '<a class="btn btn-primary" href="%s?i=i">Image</a>' % reverse('edit:correct', args=[collId, docId, 1])
#    view_links += '<a class="btn btn-primary" href="%s?i=lbl">Line by line</a>' % reverse('edit:correct', args=[collId, docId, 1])
#    view_links += '<a class="btn btn-primary" href="%s?i=sbs">Side by side</a>' % reverse('edit:correct', args=[collId, docId, 1])
#    view_links += '<a class="btn btn-primary" href="%s?i=t">Text</a>' % reverse('edit:correct', args=[collId, docId, 1])
#    view_links += '</div>'

    fulldoc = t.document(request, collId, docId,-1)

    title_desc = ''
    title_desc += '<p><b>%s</b> (%s)</p>' % (fulldoc['md']['title'], docId)
    if 'desc' in fulldoc['md']:
        title_desc += '<p id="long_text_%s">%s</p>' % (docId, fulldoc['md']['desc'])

    #Add collection of data on last saved page (aka recent)
    recent = t.document_recent(request,docId)
    if isinstance(recent,HttpResponse):
        return apps.utils.views.error_view(request,recent)

    if recent : 
        #recent will be a single item array
        recent = recent[0]
        if 'pageNr' in recent:
            title_desc += str(_('Go to <a href="%s">last saved page</a> in this document')) % reverse('edit:correct', args=[collId,recent.get('docId'),recent.get('pageNr')])

    stat_string = ''
    stat_string += '<p>%s</p>' % docStatString
    stat_string += '<p>%s</p>' % tagsString

    return JsonResponse({
            'statString': stat_string,
            'titleDesc': title_desc,
            'viewLinks': view_links
        },safe=False)

@login_required
def document_page(request, collId, docId, page=None):
    t = request.user.tsdata.t

    collection = t.collection(request, {'collId': collId})
    if isinstance(collection,HttpResponse):
        return apps.utils.views.error_view(request,collection)
    full_doc = t.document(request, collId, docId,-1)
    if isinstance(full_doc,HttpResponse):
        return apps.utils.views.error_view(request,full_doc)

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
    current_transcript = t.current_transcript(request, collId, docId, page)
    transcript = t.transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))
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



#/library/{colId}/{docId}/{page}
# view that lists transcripts in doc and some page level metadata
@login_required
def page(request, collId, docId, page):
    t = request.user.tsdata.t
    #call t_document with noOfTranscript=-1 which will return no transcript data
    full_doc = t.document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return apps.utils.views.error_view(request,full_doc)
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

#/library/{colId}/{docId}/{page}/{tsId}
# view that lists regions in transcript and some transcript level metadata
@login_required
def transcript(request, collId, docId, page, transcriptId):
    t = request.user.tsdata.t

    #t_page returns an array of the transcripts for a page
    pagedata = t.page(request, collId, docId, page)
    if isinstance(pagedata,HttpResponse):
        return apps.utils.views.error_view(request,pagedata)

    nav = navigation.up_next_prev(request,"transcript",transcriptId,pagedata,[collId,docId,page])

    pageXML_url = None;
    for x in pagedata:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break
    sys.stdout.write("PAGEXML URL : %s \r\n" % (pageXML_url) )
    sys.stdout.flush()

    if pageXML_url:
        transcript = t.transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return apps.utils.views.error_view(request,transcript)


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

#/library/{colId}/{docId}/{page}/{tsId}/{regionId}
# view that lists lines in region and some region level metadata
@login_required
def region(request, collId, docId, page, transcriptId, regionId):

    t = request.user.tsdata.t

    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would
    # rather use transciptId to target a particular transcript
    transcripts = t.page(request,collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return apps.utils.views.error_view(request,transcripts)

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t.document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return apps.utils.views.error_view(request,full_doc)

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
        transcript = t.transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return apps.utils.views.error_view(request,transcript)

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


#/library/{colId}/{docId}/{page}/{tsId}/{regionId}/{lineId}
# view that lists words in line and some line level metadata
@login_required
def line(request, collId, docId, page, transcriptId, regionId, lineId):
    t = request.user.tsdata.t
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would
    # rather use transciptId to target a particular transcript
    transcripts = t.page(request,collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return apps.utils.views.error_view(request,transcripts)
    #we are only using the transcripts to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break

    if pageXML_url:
        transcript = t.transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return apps.utils.views.error_view(request,transcript)

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t.document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return apps.utils.views.error_view(request,full_doc)

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

#/library/{colId}/{docId}/{page}/{tsId}/{regionId}/{lineId}/{wordId}
# view that shows some word level metadata
@login_required
def word(request, collId, docId, page, transcriptId, regionId, lineId, wordId):
    t = request.user.tsdata.t
    # booo hiss
    transcripts = t.page(request, collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return apps.utils.views.error_view(request,transcripts)
    #we are only using the pagedata to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break

    if pageXML_url:
        transcript = t.transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return apps.utils.views.error_view(request,transcript)

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t.document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return apps.utils.views.error_view(request,full_doc)

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
@login_required
def rand(request, collId, element):
    t = request.user.tsdata.t

    collection = t.collection(request, {'collId': collId})

    if isinstance(collection,HttpResponse):
        return apps.utils.views.error_view(request,collection)

    doc = random.choice(collection)

    collection = None
    for x in doc.get("collectionList").get("colList"):
        if str(x.get("colId")) == str(collId):
            collection = x

    pages  = t.document(request, collId, doc.get("docId"), 0)
    if isinstance(pages,HttpResponse):
        return apps.utils.views.error_view(request,pages)
    page = random.choice(pages.get("pageList").get("pages"))

    sys.stdout.write("RANDOM PAGE: %s\r\n" % (page.get("pageNr")) )
    sys.stdout.flush()

    #best to avoid a random transcript, so we'll go for the current in the hope that it is best....
    current_transcript = t.current_transcript(request, collId, doc.get("docId"), page.get("pageNr"))
    transcript = t.transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))

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

@login_required
def users(request, collId, userId):
    return render(request, 'library/users.html')

def getTagsString(personCount, placeCount, dateCount, abbrevCount, otherCount):
    if (personCount>0) or (placeCount>0) or (dateCount>0) or (abbrevCount>0) or (otherCount>0):
        tagsStringParts = []
        if personCount > 0:
            tagsStringParts += ['%i persons' % personCount]
        if placeCount > 0:
            tagsStringParts += ['%i places' % placeCount]
        if dateCount > 0:
            tagsStringParts += ['%i dates' % dateCount]
        if abbrevCount > 0:
            tagsStringParts += ['%i abbrevs ' % abbrevCount]
        if otherCount > 0:
            tagsStringParts += ['%i others' % otherCount]

        return 'Tags: ' + ', '.join(tagsStringParts)
    else:
        return 'No Tags'
