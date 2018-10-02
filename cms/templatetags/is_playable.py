from django import template
register = template.Library()

@register.simple_tag
def is_playable(content):
    return content.filepath.strip().endswith('mp4')
