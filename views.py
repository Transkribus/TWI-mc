import time

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.shortcuts import render

from apps.transkribus.mixins import LoginRequiredMixin

from . import services
from . import forms
from . import paginator
from . import models
from . import utils


def test(request):
    from django.http import HttpResponse

    if request.GET.get('error') == '1':
        # yes, we can!
        1 / 0

    return HttpResponse('test', content_type='text/plain')


def test(request):
    from django.http import HttpResponse

    if request.GET.get('error') == '1':
        # yes, we can!
        1 / 0

    return HttpResponse('test', content_type='text/plain')


class CollectionListView(LoginRequiredMixin, ListView):
    template_name = 'library/collection/list.html'
    queryset = models.Collection.objects.all()
    form_class = forms.ListForm
    paginate_by = 10
    paginator_class = paginator.Paginator

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        assert form.is_valid(), form.errors
        self.form = form
        self.search = form.cleaned_data.get('search')

        sort_by = form.cleaned_data.get('sort_by')

        qs = super(CollectionListView, self).get_queryset()

        user = self.request.user

        qs = qs.filter(user_collection__user_id=user.data.user_id)

        if self.search:
            qs = qs.filter(name__icontains=self.search)
            qs |= qs.filter(description__icontains=self.search)

        if sort_by == 'td':
            sort_by_name = '-name'
        else:
            sort_by_name = 'name'
        return qs.order_by(sort_by_name, 'description')

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(ListView, self).get_context_data(**kwargs)

        items = [
            {
                'title': item.name,
                'id': int(item.collection_id),
                'description': item.description,
                'item_count': item.documents.count(),
                'role': '',
                'thumb_url': item.thumb_url,
            } for item in context.pop('object_list')
        ]

        context.update({
            'items': items,
            'search': self.search,
            'form': self.form,
            'page': context.pop('page_obj'),
            'time_elapsed': round(1000 * (time.time() - then), 2)
        })

        return context


class DocumentListView(LoginRequiredMixin, ListView):
    template_name = 'library/document_list.html'
    form_class = forms.ListForm
    paginate_by = 10
    paginator_class = paginator.Paginator

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        assert form.is_valid(), form.errors
        self.form = form
        self.search = self.form.cleaned_data['search']

        sort_by = self.form.cleaned_data['sort_by']

        user = self.request.user

        # NOTE: respond with 404 if access denied
        collection = get_object_or_404(
            models.Collection,
            pk=self.kwargs['col_id'],
            user_collection__user_id=user.data.user_id)

        documents = collection.documents.all()

        if self.search:
            qs = documents.filter(title__icontains=self.search)
            qs |= documents.filter(author__icontains=self.search)
            qs |= documents.filter(description__icontains=self.search)
        else:
            qs = documents

        self.col_id = collection.collection_id
        self.col_name = collection.name

        if sort_by == 'td':
            sort_by_title = '-title'
        else:
            sort_by_title = 'title'
        return qs.order_by(sort_by_title, 'author', 'description')

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(ListView, self).get_context_data(**kwargs)

        items = (
            {
                'title': item.title,
                'id': int(item.docid),
                'description': item.description,
                'item_count': item.pages.count(),
                'script_type': item.scripttype.title(),
                'language': item.language.title(),
                'author': item.author,
                'writer': item.writer,
                'genre': item.genre,
                'uploader': item.uploader,
                'status': item.status,
                'created_from': item.createdfrom,
                'created_to': item.createdto,
                'thumb_url': item.thumb_url,

            } for item in context.pop('object_list')
        )

        page = context.pop('page_obj')

        col_name = self.col_name

        context.update({
            'items': items,
            'id': int(self.col_id),
            'title': col_name,
            'search': self.search,
            'form': self.form,
            'page': page,
            'time_elapsed': round(1000 * (time.time() - then), 2)
        })

        return context


class PageListView(LoginRequiredMixin, ListView):
    template_name = 'library/page/list.html'
    form_class = forms.ListForm
    paginate_by = 10

    def get_queryset(self):

        client = services.Helpers.create_client_from_request(self.request)

        form = self.form_class(self.request.GET)
        assert form.is_valid(), form.errors

        col_id = self.kwargs['col_id'] = int(self.kwargs['col_id'])
        doc_id = self.kwargs['doc_id'] = int(self.kwargs['doc_id'])

        results = services.Helpers.get_page_list(col_id, doc_id)

        self.meta_data = {
            'col': client.get_col_meta_data(col_id),
            'doc': client.get_doc_meta_data(col_id, doc_id)
        }

        self.form = form
        self.col_id = col_id
        self.doc_id = doc_id

        return results

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(ListView, self).get_context_data(**kwargs)

        items = [
            {
                'id': item.page_id,
                'thumb_url': item.thumb_url,

            } for item in context.pop('object_list')
        ]

        page = context.pop('page_obj')

        context.update({
            'items': items,
            'doc_id': self.doc_id,
            'col_id': self.col_id,
            'form': self.form,
            'page': page,
            'time_elapsed': round(1000 * (time.time() - then), 2)
        })

        return context


class CollectionDetailView(TemplateView):
    template_name = 'library/collection/detail.html'

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(CollectionDetailView, self).get_context_data(**kwargs)
        collection = models.Collection.objects.get(collection_id=context.pop('col_id'))

        context.update({
            'title': collection.name,
            'id': int(collection.collection_id),
            'description': collection.description,
            'item_count': collection.documents.count(),
            'role': '',
            'thumb_url': collection.thumb_url,
            'time_elapsed': round(1000 * (time.time() - then), 2)
        })

        return context


class DocumentDetailView(TemplateView):
    template_name = 'library/document/detail.html'

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        document = models.Document.objects.get(docid=context.pop('doc_id'))

        context.update({
            'title': document.title,
            'id': int(document.docid),
            'description': document.description,
            'item_count': document.pages.count(),
            'script_type': document.scripttype,
            'language': document.language,
            'author': document.author,
            'writer': document.writer,
            'genre': document.genre,

            'thumb_url': document.thumb_url,
            'time_elapsed': round(1000 * (time.time() - then), 2)
        })

        return context

def project_detail(request, slug_or_id):

    from django.http import Http404

    SLUGS = {
        'webuitestcollection': 2305,
        'brussels-webui-demo': 5163,
        'nekrolog': 13138,
        'kulinarik': 12710,
        'hebrew-press': 6070,
        'arabic-press-papers': 8838,
        'nz-alpine-journal': 13547,
        'tengnagel': 3850
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

    from . import services

    client = services.Helpers.create_client_from_request(request)

    from requests.exceptions import HTTPError

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

    return render(request, 'library/project_detail.html', context)
