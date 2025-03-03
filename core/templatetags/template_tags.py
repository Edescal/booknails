"""
Archivo creado para añadir tags para jinja
"""

from django import template

register = template.Library()

@register.filter
def has_tag(messages, tag):
    return any(tag in message.tags for message in messages)