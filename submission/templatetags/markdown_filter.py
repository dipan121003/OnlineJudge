import mistune
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="markdown")
@stringfilter
def markdown(value):
    return mark_safe(mistune.html(value))