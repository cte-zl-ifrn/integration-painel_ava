from django.template import Library
from django.templatetags.static import static
from django.utils.html import format_html

register = Library()


@register.simple_tag()
def boolean_icon(field_val):
    icon_rules = {True: "yes", "True": "yes", False: "no", "False": "no"}
    icon_url = static("admin/img/icon-%s.svg" % icon_rules.get(field_val, "unknown"))
    return format_html('<img src="{}" alt="{}">', icon_url, field_val)
