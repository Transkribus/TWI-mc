import time

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from . import services
from . import forms

from .legacy_views import *


class CollectionListView(LoginRequiredMixin, ListView):
    template_name = 'library/collection/list.html'
    form_class = forms.ListForm
    paginate_by = 10

    def get_queryset(self):

        client = services.Helpers.create_client_from_request(self.request)

        form = self.form_class(self.request.GET)
        assert form.is_valid(), form.errors

        self.form = form

        search = form.cleaned_data.get('search')
        sort_by = form.cleaned_data.get(
            'sort_by', self.form_class.SORT_BY_DEFAULT)

        if search not in ('', None):
            results = client.find_collections(
                query=search, sort_by=sort_by)  
        else:
            results = client.get_col_list(sort_by=sort_by)

        return results

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(ListView, self).get_context_data(**kwargs)

        items = [
            {
                'title': item.get('col_name'),
                'id': item.get('col_id'),
                'description': item.get('descr'),
                'item_count': item.get('nr_of_documents'),
                'role': item.get('role'),
                'thumb_url': item.get('thumb_url')
            } for item in context.pop('object_list')
        ]

        context.update({
            'items': items,
            'search': self.form.cleaned_data['search'],
            'form': self.form,
            'page': context.pop('page_obj'),
            'time_elapsed': round(1000 * (time.time() - then), 2)
        })

        return context


class DocumentListView(LoginRequiredMixin, ListView):
    template_name = 'library/document/list.html'
    form_class = forms.ListForm
    paginate_by = 10

    def get_queryset(self):

        client = services.Helpers.create_client_from_request(self.request)

        form = self.form_class(self.request.GET)
        assert form.is_valid(), form.errors

        col_id = self.kwargs['col_id'] = int(self.kwargs['col_id'])
        search = form.cleaned_data.get('search')
        sort_by = form.cleaned_data.get(
            'sort_by', self.form_class.SORT_BY_DEFAULT)

        if search is not None:
            results = client.find_documents(
                col_id, query=search, sort_by=sort_by)
        else:
            results = client.get_doc_list(col_id, sort_by=sort_by)

        self.meta_data = client.get_col_meta_data(col_id)

        self.form = form
        self.col_id = col_id
        self.search = search

        return results

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(ListView, self).get_context_data(**kwargs)

        items = [
            {
                'title': item.get('title'),
                'id': item.get('doc_id'),
                'description': item.get('desc'),
                'item_count': item.get('nr_of_pages'),
                'script_type': item.get('script_type'),
                'language': item.get('language'),
                'author': item.get('author'),
                'writer': item.get('writer'),
                'genre': item.get('genre'),

                'thumb_url': item.get('thumb_url'),

                # 'upload_timestamp':1472468970284,
                # 'uploader':'testuser@example.org',
                # 'uploader_id':42,
                # 'url':'https://dbis-thure.uibk.ac.at/f/Get?id=ERPDNPGLDFALSYJFLARZDNOX&fileType=view',

                # 'status': 0,
                # 'created_from_timestamp':-5993089570326,
                # 'created_to_timestamp':-5961467170326,
                # 'collection_list'

            } for item in context.pop('object_list')
        ]

        page = context.pop('page_obj')

        col_name = self.meta_data.col_name

        context.update({
            'items': items,
            'id': self.col_id,
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
