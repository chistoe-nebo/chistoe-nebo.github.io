# encoding=utf-8

"""Simple navigation menu plugin for Poole

This plugins adds the `simple_menu` function which renders a simple UL/LI based
menu which includes all pages which have properties "menu-position" and
"title".  Pages are sorted by the "menu-position" property (must be an
integer).   The LI element of the current page has the "active" class.

To insert the menu, add this to your template:

    {{ simple_menu() }}

Example output:

    <ul id="menu">
    <li class="active"><a href="/index.html"><span>Home</span></a></li>
    <li><a href="/about.html"><span>About</span></li>
    </ul>

Page property `menu-prefix` controls which pages mark the particular menu item
as active.  Imagine a menu item defined as:

    title: Photos
    menu-position: 5
    menu-prefix: /photo/

This menu item will be active on all pages that start with "/photo/".
"""

import sys

from plugins import fix_url, macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"


def simple_menu():
    pages = []

    for page in macros("pages", []):
        if "menu-position" not in page:
            continue
        if "title" not in page:
            continue
        if "draft" in page.get("labels", ""):
            continue

        pages.append((
            fix_url(page.url).lstrip("/"),
            page.get("menu-title", page["title"]),
            page.get("menu-prefix"),
            int(page.get("menu-position", 0)),
            page.get("menu-key"),
            ))

    extra = macros("SIMPLE_MENU_FIXED")
    if isinstance(extra, list):
        pages += extra
    elif extra is not None:
        print "warning: bad format of SIMPLE_MENU_FIXED"

    pages.sort(key=lambda p: int(p[3]))

    current_url = macros("page").url

    menu = u"<ul id=\"menu\">\n"
    for m_url, m_title, m_prefix, m_position, m_key in pages:
        cls = "inactive"
        if m_url == current_url:
            cls = "active"
        elif m_prefix is not None and current_url.startswith(m_prefix):
            cls = "active"
        menu += u"<li class=\"%s\">" % cls

        attrs = " title='%s'" % m_title
        if m_key:
            attrs += " accesskey='%s'" % m_key

        menu += u"<a href=\"/%s\"%s><span>%s</span></a>" \
            % (m_url, attrs, m_title)
        menu += u"</li>\n"
    menu += u"</ul>\n"

    return menu


__all__ = [
    "simple_menu",
]
