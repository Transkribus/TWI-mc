import time

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from . import services
from . import forms
from . import paginator
from . import models

from .models import Collection, Document, DocumentCollection

from .legacy_views import *


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

        qs = super(CollectionListView, self).get_queryset()

        user = self.request.user
        trp_user_id = user.tsdata.userId

        qs = qs.filter(user_collection__user_id=trp_user_id)

        if self.search:
            qs = qs.filter(name__icontains=self.search)
            qs |= qs.filter(description__icontains=self.search)

        return qs.order_by('name', 'description')

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

        user = self.request.user
        trp_user_id = user.tsdata.userId

        # NOTE: respond with 404 if access denied
        collection = get_object_or_404(
            models.Collection,
            pk=self.kwargs['col_id'],
            user_collection__user_id=trp_user_id)

        documents = collection.documents.all()

        if self.search:
            qs = documents.filter(title__icontains=self.search)
            qs |= documents.filter(author__icontains=self.search)
            qs |= documents.filter(description__icontains=self.search)
        else:
            qs = documents

        self.col_id = collection.collection_id
        self.col_name = collection.name

        return qs.order_by('title', 'author', 'description')

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


class CollectionView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(ListView, self).get_context_data(**kwargs)
        collection = Collection.objects.get(collection_id=context.pop('col_id'))

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


def collection_detail(request, col_id):
    from django.http import HttpResponse
    return HttpResponse("Not Implemented", status=501)

def document_detail(request, col_id, doc_id):
    from django.http import HttpResponse
    return HttpResponse("Not Implemented", status=501)

@login_required
def project(request, slug):
    from django.http import HttpResponseNotFound

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
