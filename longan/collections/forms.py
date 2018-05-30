from django import forms

from . import models


class ListForm(forms.Form):

    PAGE_MIN = 1
    SIZE_MIN = 1
    SIZE_MAX = 100
    SIZE_DEFAULT = 10

    SORT_BY = {
        'ta': "Title: ascending",
        'td': "Title: descending"
    }

    SORT_BY_DEFAULT = 'ta'

    sort_by = forms.TypedChoiceField(
        choices=SORT_BY.items(),
        coerce=str,
        empty_value=SORT_BY_DEFAULT,
        required=False,
        widget = forms.Select(attrs = {
            'onchange' : 'this.form.submit()',
        })
    )

    search = forms.CharField(max_length=42, required=False)

    page = forms.IntegerField(
        min_value=PAGE_MIN,
        required=False,
        widget=forms.HiddenInput({'value': PAGE_MIN})
    )

    size = forms.IntegerField(
        initial=SIZE_MIN,
        min_value=SIZE_MIN,
        max_value=SIZE_MAX,
        required=False,
        widget=forms.HiddenInput({'value': SIZE_DEFAULT})
    )
