from django.core import paginator

class Page(paginator.Page):

    page_range_width = 5

    @property
    def page_range(self):

        # NOTE: usually, there is no page_range on Page class

        width = self.page_range_width
        num_pages = self.paginator.num_pages

        start = max(1, self.number - int(width / 2))
        length = min(width, num_pages)

        delta = (start + length - 1) - num_pages

        if delta > 0:
           start -= delta

        return range(start, start + length)

    @property
    def is_first_in_range(self):
        # NOTE: this is also non-standard
        return min(self.page_range) == 1

    @property
    def is_last_in_range(self):
        # NOTE: non-standard method
        return max(self.page_range) == self.paginator.num_pages


class Paginator(paginator.Paginator):

    def _get_page(self, *args, **kwargs):
        return Page(*args, **kwargs)

    @property
    def page_range(self):
        raise NotImplementedError("page_range not implemented")
