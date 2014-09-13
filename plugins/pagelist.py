# encoding=utf-8

import cgi
import time

from plugins import fix_url
from plugins import get_page_date
from plugins import get_page_labels
from plugins import macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"


def title_format(page):
    page_url = fix_url(page["url"])
    return u"<a href='/%s'>%s</a>" % (page_url, cgi.escape(page["title"]))


def pagelist(label=None, limit=None, date=None, order="-date"):
    """Renders and returns a list of links to pages."""

    title_fmt = macros("format_pagelist_title", title_format)

    try:
        reverse_order = order.startswith("-")
        order_field = order.lstrip("-")

        def _filter(page):
            labels = get_page_labels(page)
            if "queue" in labels or "draft" in labels:
                return False
            if label is not None and label not in labels:
                return False
            if date is not None and "date" not in page:
                return False
            if order_field not in page:
                return False
            return True

        matching_pages = sorted([p for p in macros("pages") if _filter(p)],
            key=lambda p: (p[order_field].lower(), p["url"]), reverse=reverse_order)

        if limit is not None:
            del matching_pages[limit:]

        if not matching_pages:
            return "(no matching pages)"

        months = [u"январь", u"февраль", u"март", u"апрель", u"май", u"июнь",
            u"июль", u"август", u"сентябрь", u"октябрь", u"ноябрь", u"декабрь"]

        last_year = None

        output = u"<ul class='pagelist'>\n"
        for page in matching_pages:
            page_url = fix_url(page["url"])
            page_date = get_page_date(page)

            if last_year != page_date.tm_year:
                output += u"<li class=\"sep\">"
                output += u"<span class='year'>%u</span>" % page_date.tm_year
                last_year = page_date.tm_year
            else:
                output += u"<li>"

            output += title_fmt(page)
            if date is not None:
                month = int(time.strftime("%m", page_date))
                output += u" <span class=\"month\">(%s)</span>" % months[month-1]

            output += u" <a class='disqus_count' href='/%s#disqus_thread' data-disqus-identifier='%s'>комментировать</a>" \
                % (page_url, page.url)

            output += u"</li>\n"
        output += u"</ul>\n"

        return output
    except Exception, e:
        print "error  : could not list pages: %s" % e
        return "<!-- error building the list -->"


__all__ = [
    "pagelist",
]
