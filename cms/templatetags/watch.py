from django import template
from django.utils.http import urlquote
import re

register = template.Library()

@register.filter
def quote_filepath(url):
    _, scheme, path = re.split(r'(https?://)', url)
    return '{}{}'.format(scheme, urlquote(path))
