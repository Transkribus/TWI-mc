from django.http import Http404
from django.shortcuts import render

from requests.exceptions import HTTPError

from . import utils
from . import services

def project_list(request):
    return render(request, template_name='projects/project_list.html')

def project_detail(request, slug_or_id):

    SLUGS = {
        'webuitestcollection': 2305,
        'brussels-webui-demo': 5163,
        'nekrolog': 13138,
        'kulinarik': 12710,
        'hebrew-press': 6070,
        'arabic-press-papers': 8838,
        'nz-alpine-journal': 13547,
        'tengnagel': 3850,
        'hazfirah': 17989
    }

    TITLES = {
        2305: 'Web UI Test Collection'
    }

    if slug_or_id.isdigit():
        col_id = int(slug_or_id)
    else:
        col_id = SLUGS.get(slug_or_id)
        if col_id is None:
            raise Http404

    client = services.Helpers.create_client_from_request(request)

    try:
        # 1 request
        collection = client.get_col_meta_data(col_id)
    except HTTPError as error:
        if error.response.status_code == 403:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Forbidden")
        elif error.response.status_code == 404:
            raise Http404

    # 2 requests
    documents = client.get_doc_list(int(collection.col_id))

    DOC_ID = 'docId'

    try:
        doc_id = int(request.GET[DOC_ID])
    except (ValueError, KeyError):
        doc_id = doc = None
    else:
        # 3 requests
        try:
            doc = client.get_fulldoc(collection.col_id, doc_id)
        except HTTPError as error:
            doc_id = doc = None
        
    # 4th request
    stats = utils.Stats(client.get_col_stats(collection.col_id))    

    context = {
        'slug': slug_or_id,
        'collection': {
            'id': collection.col_id,
            'name': collection.col_name,
            'num_docs': collection.nr_of_documents,
            'title': TITLES.get(collection.col_id),
            'progress': stats.progress
        },
        'selected_document_id': doc_id,
        'selected_document': None if doc is None else {
            'id': doc.md['docId'],
            'title': doc.md['title'],
            'num_pages': doc.md['nrOfPages'],
            'progress': utils.Stats(doc.md).progress,
            'pages': utils.PageList(doc)
        },
        'documents':({
            'id': doc.doc_id,
            'status': doc.status,
            'title': doc.title
        } for doc in documents)
    }

    return render(request, 'projects/project_detail.html', context)
