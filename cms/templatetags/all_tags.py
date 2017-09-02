from django import template

from cms.models import Tag

register = template.Library()

@register.assignment_tag
def get_all_tags():
    return Tag.objects.order_by('name').all()
