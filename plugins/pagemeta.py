# encoding=utf-8

import cgi
import time

from plugins import get_page_date
from plugins import get_page_labels
from plugins import macros
from plugins.authors import get_page_author


def page_meta():
    """Renders the page metadata block."""
    parts = []

    page = macros("page")

    if macros("PAGEMETA_DATE_ONLY", True) and "date" not in page:
        return ""

    wanted_labels = macros("PAGEMETA_LABELS", ["blog", "photo"])

    labels = get_page_labels(page)
    if not set(wanted_labels) & set(labels):
        return ""

    author = get_page_author(page)
    sex_idx = 1 if author.get("sex") == "f" else 0

    if author is not None:
        name = author.get("display_name", author.get("name"))

        if "photo" in labels:
            part = (u"Фотографию загрузил ", u"Фотографию загрузила ")[sex_idx]
        else:
            part = (u"Заметку написал ", u"Заметку написала ")[sex_idx]

        if author.get("url"):
            part += u"<a rel='author' href='%s'>%s</a>" % (
                cgi.escape(author["url"]), cgi.escape(name))
        else:
            part += cgi.escape(name)

        pd = get_page_date(page)
        if pd is not None:
            months = [u"января", u"февраля", u"марта", u"апреля", u"мая", u"июня",
                u"июля", u"августа", u"сентября", u"октября", u"ноября", u"декабря"]
            month = int(time.strftime("%m", pd))
            part += u", <time datetime='%s'>%s %s %s года</time>" % (
                time.strftime("%Y-%m-%d", pd), time.strftime("%d", pd),
                months[month-1], time.strftime("%Y", pd))

        parts.append(part)

    """
    labels = get_page_labels(page)
    if labels and "photo" not in labels:
        labels = [_get_label_info(l) for l in labels]
        printable = [_format_label(l) for l in sorted(labels, key=lambda l: l[1].lower())]
        parts.append(u"метки: %s" % u", ".join(printable))
    """

    if "youtube-views" in page:
        parts.append(u"%s просмотров" % page["youtube-views"])

    if not parts:
        return ""

    return u"<p class='meta pagemeta'>%s.</p>" % u"; ".join(parts)


__all__ = [
    "page_meta",
]
