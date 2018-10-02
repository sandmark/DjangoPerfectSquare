from django import template
from django.contrib.auth.models import User
from cms.models import Content, Check

register = template.Library()

@register.simple_tag
def user_checked(user, content):
    return Check.objects.filter(user=user, content=content).first()

@register.simple_tag
def format_date(checked, string='{:%Y-%m-%d}'):
    return string.format(checked.date)
