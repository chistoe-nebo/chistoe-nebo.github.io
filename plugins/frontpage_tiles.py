# encoding=utf-8

import os

from plugins import macros, get_page_labels, Tiles, Thumbnail
from plugins import get_page_image_path
from plugins import fix_url


__all__ = [
    "frontpage_tiles",
]


def take(n, args):
    args = args + (None,) * n
    return args[:n]


def find_pages(label, skip=None):
    pages = []
    skip = set((skip or []) + ["draft"])

    for page in macros("pages"):
        labels = get_page_labels(page)
        if label not in labels:
            continue
        if set(labels) & skip:
            continue
        pages.append(page)

    return sorted(pages,
        key=lambda p: p.get("date"),
        reverse=True)


def frontpage_tiles():
    """Вывод блоков на главной странице"""
    specs = macros("FRONTPAGE_SPECS", [])

    columns = []

    for spec in specs:
        try:
            label = spec["label"]
            title = spec["title"]
            more = spec["more"]
            skip = spec.get("skip", [])
        except KeyError, e:
            print "warning: block spec has no '%s': %s" % (e.args[0], spec)
            continue

        col_idx = (len(columns) % 3) + 1
        column = u"<div class='column col_%u'>\n" % col_idx

        column += u"<h2>%s</h2>\n" % title

        pages = find_pages(label, skip)
        if not pages:
            continue

        column += u"<ul>\n"
        for idx, page in enumerate(pages[:6]):
            image_path = get_page_image_path(page)

            column += u"<li>\n"

            link = u"<a href='/%s'" % fix_url(page.url)

            title = page.get("short-title", page["title"])

            if idx == 0 and image_path:
                link += u" class='tile'"

                t = Thumbnail(image_path,
                    width=300, height=200)
                link += u" style='background-image: url(/%s)'" % t.web_path

            if "summary" in page:
                link += u" title='%s'" % page["summary"]

            column += u"%s><span>%s</span></a>\n" % (link, title)

            column += u"</li>\n"
        column += u"</ul>\n"

        if len(pages) > 6 and more:
            column += u"<p class='more'>%s</p>" % more

        column += u"</div>\n"
        columns.append(column)

    if not columns:
        return ""

    html = u""
    while columns:
        html += u"<div class='columns'>\n"
        html += u"\n".join(columns[:3])
        html += u"</div>\n"
        del columns[:3]

    return html
