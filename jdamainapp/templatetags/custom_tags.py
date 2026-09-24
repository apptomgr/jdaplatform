from django import template
from django.utils import translation

register = template.Library()

@register.simple_tag(takes_context=True)
def get_current_language(context):
    return translation.get_language()

@register.filter
def has_group(user, group_name):
    """Usage: {% if user|has_group:"Sales Staff" %} ... {% endif %}"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()