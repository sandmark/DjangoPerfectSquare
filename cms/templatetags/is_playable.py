from django import template
register = template.Library()

@register.assignment_tag
def is_playable(content):
    return content.filepath.strip().endswith('mp4')
