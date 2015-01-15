# encoding=utf-8

"""META injector for Poole

This plugin adds useful META keywords to all pages.  To use it, load the script
in macros.py like this:

    from plugins.meta import *

Keywords are specified in the pages, like this:

    title: Some page
    keywords: light bulb, howto
    description: Instructions on installing a light bulb.

This script also automatically adds the canonical link, which is produced by
adding page URL to BASE_URL (from macros.py), then passing the result through
the fix_url function (again from macros.py), if one exists.  This way you can
inform search engines that you prefer URLS without index.html, even though your
web server replies to both.
"""


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"

import cgi
import Image
import mimetypes
import os
import sys
import time
import urlparse

from plugins import macros, get_page_date, get_page_url, fix_url


def _is_podcast(page):
    return page.get("file", "").endswith(".mp3")


def quote(string):
    return cgi.escape(string)


def hook_html_meta_keywords(html):
    """Adds meta keywords.  The canonical link is only added if it differs from
    the original page URL (i.e., if BASE_URL is defined and if fix_url() does
    something)."""
    keywords = u""

    page = macros("page")

    if "summary" in page:
        keywords += u"<meta name='description' content='%s'/>\n" % cgi.escape(page["summary"])
    if "keywords" in page:
        keywords += u"<meta name='keywords' content='%s'/>\n" % cgi.escape(page["keywords"])

    page_url = get_page_url(page)
    if page_url != page["url"]:
        keywords += u"<link rel='canonical' href='%s'/>\n" % page_url

    if keywords:
        html = html.replace("</head>", keywords + "</head>")

    return html


def get_page_image(page):
    base_url = macros("BASE_URL")
    if not base_url:
        return None

    page_url = urlparse.urljoin(base_url, page.url)

    for k in ("image", "thumbnail", "picture"):
        if page.get(k):
            image_url = urlparse.urljoin(page_url, page[k])
            return fix_url(image_url)

    return None


def hook_html_opengraph(html):
    """Adds OpenGraph metadata to the current page.
    Example: https://github.com/niallkennedy/open-graph-protocol-examples/blob/master/article-utc.html
    """
    page = macros("page")

    tags = []

    def add_tag(k, v):
        try:
            if isinstance(v, str):
                v = v.decode("utf-8")
            tags.append((u"<meta property=\"{0}\" " \
                u"content=\"{1}\"/>").format(k, quote(v)))
        except Exception, e:
            print(e, k, v)

    basic = [("OG_COUNTRY_NAME", "og:country-name"),
        ("WEBSITE_NAME", "og:site_name"),
        ("OG_LOCALITY", "og:locality"),
        ("OG_EMAIL", "og:email")]
    for var, tag in basic:
        value = macros(var)
        if value:
            add_tag(tag, value)

    if "title" in page:
        add_tag("og:title", page["title"])

    if "summary" in page:
        add_tag("og:description", page["summary"])

    lang = page.get("lang", macros("DEFAULT_LANGUAGE", "en"))
    if lang == "en":
        add_tag("og:locale", "en_US")
    elif lang == "ru":
        add_tag("og:locale", "ru_RU")

    add_tag("og:url", get_page_url(page))

    if "blog" in page.get("labels", ""):
        author = page.get("author")
        author_link = macros("AUTHOR_LINKS", {}).get(author)
        if author_link:
            add_tag("og:author", author_link)

        if "tags" in page:
            for tag in page["tags"].split(","):
                if not tag.strip():
                    continue
                add_tag("article:tag", tag.strip())

        if "date" in page:
            date = get_page_date(page)
            add_tag("article:published_time",
                time.strftime("%Y-%m-%dT%H:%M:%SZ", date))

    if _is_podcast(page):
        url = urlparse.urljoin(macros("BASE_URL"), page["file"].decode("utf-8"))
        add_tag("og:audio", url)
        add_tag("og:audio:type", "audio/mp3")

    image_url = get_page_image(page) or macros("OG_DEFAULT_IMAGE")
    if image_url:
        add_tag("og:image", fix_url(image_url))

        """
        img = Image.open(image_path)
        add_tag("og:image:width", str(img.size[0]))
        add_tag("og:image:height", str(img.size[1]))
        """

        mt, subtype = mimetypes.guess_type(image_url)
        if mt:
            add_tag("og:image:type", mt)

    # TODO: og:section

    tags_html = u"\n".join(tags)
    if isinstance(html, str):
        tags_html = tags_html.encode("utf-8")

    html = html.replace("</head>",
        tags_html + "\n</head>")

    prefix = " prefix=\"og: http://ogp.me/ns# " \
        "article: http://ogp.me/ns/article#\""
    if "<head>" in html:
        html = html.replace("<head>", "<head" + prefix + ">")
    else:
        html = html.replace("<head ", "<head" + prefix + " ")

    return html


__all__ = [
    "hook_html_meta_keywords",
    "hook_html_opengraph",
]
