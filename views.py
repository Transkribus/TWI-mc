import time

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from . import services
from . import forms
from . import paginator

from .models import Collection, Document, DocumentCollection

from .legacy_views import *


class CollectionListView(LoginRequiredMixin, ListView):
    template_name = 'library/collection/list.html'
    form_class = forms.ListForm
    paginate_by = 10
    paginator_class = paginator.Paginator

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        assert form.is_valid(), form.errors
        self.form = form
        self.search = form.cleaned_data.get('search')

        if self.search:
            collections = Collection.objects.filter(\
                Q(name__icontains=self.search) |\
                Q(description__icontains=self.search)\
            )
        else:
            collections = Collection.objects.all()

        return collections

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
    template_name = 'library/document/list.html'
    form_class = forms.ListForm
    paginate_by = 10
    paginator_class = paginator.Paginator

    def get_queryset(self):
        form = self.form_class(self.request.GET)
        assert form.is_valid(), form.errors
        self.form = form
        self.search = self.form.cleaned_data['search']

        if self.search:
            documents = Document.objects.filter(\
                Q(title__icontains=self.search) |\
                Q(author__icontains=self.search) |\
                Q(description__icontains=self.search)\
            )
        else:
            documents = Document.objects.all()

        collection = DocumentCollection.objects.filter(docid=documents[0].docid).first().collection
        self.col_id = collection.collection_id
        self.col_name = collection.name

        return documents

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(ListView, self).get_context_data(**kwargs)

        items = [
            {
                'title': item.title,
                'id': int(item.docid),
                'description': item.description,
                'item_count': item.pages.count(),
                'script_type': item.scripttype,
                'language': item.language,
                'author': item.author,
                'writer': item.writer,
                'genre': item.genre,

                'thumb_url': item.thumb_url,

            } for item in context.pop('object_list')
        ]

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

def collection_detail(request, col_id):
    from django.http import HttpResponse
    return HttpResponse("Not Implemented", status=501)

def document_detail(request, col_id, doc_id):
    from django.http import HttpResponse
    return HttpResponse("Not Implemented", status=501)


@login_required
def project(request, slug):
    t = request.user.tsdata.t

    slugs = {
        'webuitestcollection': 2305,
        'brussels-webui-demo': 5163,
    }

    if slug not in slugs:
        return HttpResponseNotFound('No collection found with "%s".' % slug)

    metadata = t.collection_metadata(request,{'collId': slugs[slug]})
    col_name = metadata['colName']
    col_id = metadata['colId']
    documents = []
    for d in t.collection(request, {'collId': slugs[slug]}):
        if d['status'] == 0:
            status = _('New')
        elif d['status'] == 1:
            status = _('In Progress')
        elif d['status'] == 2:
            status = _('Done')
        elif d['status'] == 3:
            status = _('Final')
        else:
            status = _('Ground Truth')
        documents.append({
            'title': d['title'],
            'doc_id': d['docId'],
            'status': status
        })

    return render(request, 'library/project.html', locals())
