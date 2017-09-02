from django import template

from cms.models import Tag

register = template.Library()

@register.assignment_tag
def get_all_tags():
    return Tag.objects.all().order_by('name')
