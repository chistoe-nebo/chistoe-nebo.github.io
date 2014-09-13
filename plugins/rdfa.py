# encoding=utf-8

"""RDFa ImageObject support for Markdown

With this plugin enabled, embedded images are wrapped in a DIV element
with proper RDFa attributes.  Example code:

    ![A bird](/photo/bird.jpg)

Result:

    <div itemscope="itemscope" itemtype="http://schema.org/ImageObject">
        <a href="/photo/bird.html">
            <img src="/photo/bird.jpg" itemprop="contentUrl" alt="A bird" />
        </a>
    </div>
"""

from __future__ import print_function

import Image
import os
import re
import urlparse

import markdown.inlinepatterns

import macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"


def has_page(img_url):
    if "://" in img_url:
        # print("debug  : %s is an external image" % img_url)
        return False

    """
    if not img_url.startswith("/"):
        import macros
        print("warning: %s -- relative image url in %s" % (img_url, macros.page.fname))
    """

    base = "input/" + os.path.splitext(img_url)[0].lstrip("/")
    if os.path.exists(base + ".html"):
        return True
    elif os.path.exists(base + ".txt"):
        return True
    elif os.path.exists(base + ".md"):
        return True

    # print("warning: please create %s.txt" % base)
    return False


def abshref(href):
    if href.startswith("/"):
        return href

    if "://" in href:
        return href

    return "/" + urlparse.urljoin(macros.page.url, href)


def new_image_reference_tag(self, href, title, text):
    parent = wr = markdown.etree.Element("figure")
    wr.set("itemscope", "itemscope")
    wr.set("itemtype", "http://schema.org/ImageObject")
    wr.set("class", "figure")

    href = abshref(href)

    img_has_page = has_page(href)
    img_page_url = href[:-3] + "html"

    if img_has_page:
        parent = markdown.etree.SubElement(wr, "a")
        parent.set("title", title or text)
        parent.set("href", img_page_url)

    el = markdown.etree.SubElement(parent, "img")
    el.set("itemprop", "contentUrl")
    el.set("src", self.sanitize_url(href))
    if title:
        el.set("title", title)
    el.set("alt", text)
    if img_has_page:
        el.set("longdesc", img_page_url)

    img_path = "input" + href
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            el.set("style", "width:%upx;height:%upx" % img.size)
        except Exception, e:
            print("error  : could not get image size: %s" % e)

    if title:
        desc = markdown.etree.SubElement(wr, "figuredesc")
        desc.set("class", "imgdesc")
        desc.set("itemprop", "description")
        desc.text = title

    return wr

markdown.inlinepatterns.ImageReferencePattern.makeTag = new_image_reference_tag


def new_image_tag(self, m):
    href = title = text = None

    src_parts = m.group(9).split()
    if src_parts:
        href = src_parts[0]
        if href[0] == "<" and href[-1] == ">":
            href = href[1:-1]
    if len(src_parts) > 1:
        title = markdown.inlinepatterns.dequote(" ".join(src_parts[1:]))

    text = m.group(2)

    return new_image_reference_tag(self, href, title, text)

markdown.inlinepatterns.ImagePattern.handleMatch = new_image_tag


print("info   : added RDFa ImageObject support to Markdown.")


def hook_html_fix_figure(html):
    html = re.sub(r"<p>\s*<figure", "<figure", html, flags=re.S)
    html = re.sub(r"</figure>\s*</p>", "</figure>", html, flags=re.S)
    return html


__all__ = [
    "hook_html_fix_figure",
]
