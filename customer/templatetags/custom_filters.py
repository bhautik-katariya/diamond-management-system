from django import template
from urllib.parse import urlencode, parse_qs, urlparse

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def add_sort(current_url, sort_value):
    url_parts = urlparse(current_url)
    query_dict = parse_qs(url_parts.query)
    query_dict['sort'] = [sort_value]
    return f"{url_parts.path}?{urlencode(query_dict, doseq=True)}"
