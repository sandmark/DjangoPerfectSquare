from django import template

from cms.models import Tag

register = template.Library()

@register.assignment_tag
def get_all_tags():
    tags = Tag.objects.all().order_by('name')
    return sorted(tags, key=lambda tag: tag.name)
