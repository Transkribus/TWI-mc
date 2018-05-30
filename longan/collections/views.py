import time

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.shortcuts import render

from transkribus.mixins import LoginRequiredWithCookieMixin

from . import forms
from . import paginator
from . import models


class CollectionListView(LoginRequiredWithCookieMixin, ListView):
    template_name = 'collections/collection_list.html'
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
                'id': int(item.id),
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


class DocumentListView(LoginRequiredWithCookieMixin, ListView):
    template_name = 'collections/document_list.html'
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

        self.col_id = collection.id
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
                'id': int(item.id),
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


class PageListView(LoginRequiredWithCookieMixin, ListView):
    template_name = 'collections/page_list.html'
    form_class = forms.ListForm
    paginator_class = paginator.Paginator
    paginate_by = 10

    def get_queryset(self):

        from django.db.models import Max

        FIELDS = (
            'id', 'page_id', 'status', 'timestamp',
            'page_nr', 'page__imagekey',
            'user',
            'toolname'
        )

        doc_id = 459
        sort_by_fields = ('page_nr', )

        qs = models.Transcript.objects.filter(doc_id=doc_id)

        qs = qs.values('page_id').annotate(
            most_recent=Max('timestamp')).order_by(*sort_by_fields).values(*FIELDS)

        # NOTE: this is the test for correctness,
        #
        # for actual in qs:
        #
        #     page_id = actual['page_id']
        #
        #     expected = models.Transcript.objects.filter(
        #         doc_id=doc_id, page_id=page_id
        #     ).order_by('-timestamp')[0]
        #
        #     assert actual['id'] == expected.id

        return qs

    def get_context_data(self, **kwargs):

        context = super(PageListView, self).get_context_data(**kwargs)

        from . import helpers

        items = [
            {
                'page_nr': int(item['page_nr']),
                'status': item['status'],
                'thumb_url': helpers.get_thumb_url(
                    item['page__imagekey']),
                'username': item['user'],
                'toolname': item['toolname'],
            } for item in context.pop('object_list')
        ]

        # assert False, context['page_obj'].paginator.num_pages

        context.update({
            'col_id': self.kwargs['col_id'],
            'doc_id': self.kwargs['doc_id'],
            'items': items,
            'page': context.pop('page_obj')
        })

        return context


class CollectionDetailView(TemplateView):
    template_name = 'collections/collection_detail.html'

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(CollectionDetailView, self).get_context_data(**kwargs)
        collection = models.Collection.objects.get(id=context.pop('col_id'))

        context.update({
            'title': collection.name,
            'id': int(collection.id),
            'description': collection.description,
            'item_count': collection.documents.count(),
            'role': '',
            'thumb_url': collection.thumb_url,
            'time_elapsed': round(1000 * (time.time() - then), 2)
        })

        return context


class DocumentDetailView(TemplateView):
    template_name = 'collections/document_detail.html'

    def get_context_data(self, **kwargs):
        then = time.time()

        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        document = models.Document.objects.get(id=context.pop('doc_id'))

        context.update({
            'title': document.title,
            'id': int(document.id),
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
