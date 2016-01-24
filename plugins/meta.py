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
import re
import sys
import time
import urlparse

from plugins import macros, get_page_date, get_page_url, fix_url, join_path


def _is_podcast(page):
    return page.get("file", "").endswith(".mp3")


def _has_image(page):
    return "image" in page


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

    if "prev" in page:
        link = fix_url(page["prev"]["url"])
        keywords += u"<link rel='prev' href='/%s'/>\n" % link

    if "next" in page:
        link = fix_url(page["next"]["url"])
        keywords += u"<link rel='next' href='/%s'/>\n" % link

    if keywords:
        html = html.replace("</head>", keywords + "</head>")

    return html


def hook_html_opengraph(html):
    """Adds OpenGraph metadata to the current page.
    Example: https://github.com/niallkennedy/open-graph-protocol-examples/blob/master/article-utc.html
    """
    page = macros("page")

    tags = []
    ns = ["og: http://ogp.me/ns#"]

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

    if page.url == "index.html":
        # https://developers.facebook.com/docs/reference/opengraph/object-type/website/
        add_tag("og:type", "website")
        ns.append("website: http://ogp.me/ns/website#")

    elif "item" in page.get_labels():
        # https://developers.facebook.com/docs/reference/opengraph/object-type/product/
        ns.append("product: http://ogp.me/ns/product#")

        add_tag("og:type", "product")
        add_tag("product:price:amount", str(page.get("price", 0)))
        add_tag("product:price:currency", "RUB")
        add_tag("product:shipping_cost:amount", "300")
        add_tag("product:shipping_cost:currency", "RUB")
        if page.get("group"):
            add_tag("product:category", page["group"])

    else:
        # https://developers.facebook.com/docs/reference/opengraph/object-type/article/
        add_tag("og:type", "article")
        ns.append("article: http://ogp.me/ns/article#")

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

    images = page.find_images()
    if images:
        image = images[0]

        for img in images:
            if img["name"] == page.get("image"):
                image = img

        image_path = image["path"]
        image_url = image["url"]
        image_url = urlparse.urljoin(macros("BASE_URL"), image_url)
        add_tag("og:image", fix_url(image_url))

        img = Image.open(image_path)
        add_tag("og:image:width", str(img.size[0]))
        add_tag("og:image:height", str(img.size[1]))

        mt, subtype = mimetypes.guess_type(image_path)
        if mt:
            add_tag("og:image:type", mt)

    # TODO: og:section

    tags_html = u"\n".join(tags)
    if isinstance(html, str):
        tags_html = tags_html.encode("utf-8")

    html = html.replace("</head>",
        tags_html + "\n</head>")

    prefix = " prefix=\"%s\"" % " ".join(ns)
    if "<head>" in html:
        html = html.replace("<head>", "<head" + prefix + ">")
    else:
        html = html.replace("<head ", "<head" + prefix + " ")

    return html


def hook_html_prefetch(html):
    items = re.findall(r"data-prefetch='([^']+)'", html, re.U|re.M)
    items += re.findall(r'data-prefetch="([^"]+)"', html, re.U|re.M)

    if items:
        items = sorted(list(set(items)))
        meta = ["<link rel=\"prefetch\" href=\"%s\"/>\n" % i for i in items]
        meta = "".join(meta)
        html = html.replace("</head>", meta + "</head>")

    return html


def hook_html_twitter_cards(html):
    page = macros("page")

    if page.is_hidden():
        return html

    if "item" in page.get_labels():
        # https://cards-dev.twitter.com/validator
        add = u"<meta name='twitter:card' content='summary_large_image'/>\n"
        add += u"<meta name='twitter:site' content='@umonkey'/>\n"
        add += u"<meta name='twitter:creator' content='@umonkey'/>\n"
        """
        # No need to duplicate -- OGP fallback works.
        add += u"<meta name='twitter:title' content='%s'/>\n" % page["title"]
        if page.get("summary"):
            add += u"<meta name='twitter:description' content='%s'/>\n" % page["summary"]
        for image in page.find_images():
            add += u"<meta name='twitter:image' content='%s/%s'/>\n" \
                % (macros("BASE_URL"), image["url"])
        """
        html = html.replace("</head>", add + "</head>")

    return html


__all__ = [
    "hook_html_meta_keywords",
    "hook_html_opengraph",
    "hook_html_prefetch",
    "hook_html_twitter_cards",
]
