from django import template
from django.template.defaultfilters import stringfilter
import math

register = template.Library()

@register.filter
def millennium(value):
    if str(value).startswith('-'):
        value = str(value)[1:]
        value = math.ceil(float(value) / 1000)
        return value*-1
    else:
        return math.ceil(float(value)/1000)
    
    
'''
https://stackoverflow.com/questions/45011440/translating-dynamic-content-in-django-templates
'''    
@register.filter(name='template_trans')
def template_trans(text):
    try:
        return ugettext(text)
    except:
        return text    