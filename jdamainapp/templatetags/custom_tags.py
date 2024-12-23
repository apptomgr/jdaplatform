from django import template
from django.utils import translation

register = template.Library()

@register.simple_tag(takes_context=True)
def get_current_language(context):
    return translation.get_language()