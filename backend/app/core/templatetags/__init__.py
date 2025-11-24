from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Custom template filter to lookup dictionary values"""
    if dictionary and key:
        return dictionary.get(key, '')
    return ''
