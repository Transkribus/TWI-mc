from django.core import paginator

class Page(paginator.Page):

    page_range_width = 5

    def page_range(self):
        width = self.page_range_width
        start = max(1, self.number - int(width / 2))
        num_pages = self.paginator.num_pages
        stop = start + self.page_range_width
        return range(start, stop)

class Paginator(paginator.Paginator):

    def _get_page(self, *args, **kwargs):
        return Page(*args, **kwargs)

    @property
    def page_range(self):
        raise NotImplementedError("page_range not implemented")
