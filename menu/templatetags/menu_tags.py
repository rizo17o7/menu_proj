# menu/templatetags/menu_tags.py

from django import template
from django.urls import reverse
from django.utils.html import format_html

from menu.models import Menu, MenuItem

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    try:
        menu = Menu.objects.get(name=menu_name)
        menu_items = MenuItem.objects.filter(menu=menu).select_related('parent')
        request = context['request']
        current_path = request.path
        menu_html = build_menu_html(menu_items, current_path)
        return format_html(menu_html)
    except Menu.DoesNotExist:
        return ''


def build_menu_html(menu_items, current_path):
    def render_item(item):
        url = item.url if item.url else reverse(item.named_url)
        children = render_children(item)
        active_class = 'active' if current_path == url else ''
        return f'<li class="{active_class}"><a href="{url}">{item.title}</a>{children}</li>'

    def render_children(parent):
        children = [render_item(item) for item in menu_items if item.parent == parent]
        if children:
            return '<ul>' + ''.join(children) + '</ul>'
        return ''

    root_items = [item for item in menu_items if item.parent is None]
    return '<ul>' + ''.join(render_item(item) for item in root_items) + '</ul>'
