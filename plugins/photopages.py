# vim: set fileencoding=utf-8 ft=python:

"""Photo pages plugin for Poole

This plugin helps dealing with JPEG photo.  It creates virtual pages for JPEG
files, has template functions to embed photo albums and separate thumbnails. 
To use it, load the script and configure it, like this:

    from plugins.photopages import *
    PHOTO_PAGE_TEMPLATE = "photo.md"  # required
    PHOTO_INCLUDE = "^photo/[^/]+\.(jpg|jpeg)$"  # optional
    PHOTO_THUMBNAIL_FOLDER = "output/thumbnails"  # optional

Photo albums are embedded like this:

    {{ photo_album(split_months=True, size=75) }}

The 'split_months' option enabled splitting the list of thumbnails by monthly
headers, like "2012/08"; 'size' is the size of thumbnail (square).  Thumbnails
link to pages with full-sized images; URL of the full-sized image is also
stored in the 'data-large-img' link attribute, for use with JavaScript image
libraries such as Thickbox.
"""

import hashlib
import os
import re
import shutil
import sys
import time

from PIL import Image

import markdown

from plugins import Page
from plugins import macros, fix_url, fix_url_unicode, get_page_date, Tiles, Thumbnail
from plugins import get_page_labels


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"

PHOTOALBUM_ITEM_TEMPLATE = " <li class=\"thumbnail\">\n%s </li>\n"
PHOTO_THUMBNAIL_TEMPLATE = "  <a href='/%(link)s' title='%(title)s' rel='shadowbox[%(album_id)s];content=%(large)s;player=img'>\n   <img src='%(img_uri)s' alt='%(title)s'/>\n  </a>\n"

PHOTO_THUMBNAIL_FOLDER = "output/thumbnails"
PHOTO_INCLUDE_PATTERN = "\.(jpg|jpeg)$"


class Photos(object):
    pages = None

    @classmethod
    def all(cls):
        if cls.pages is None:
            cls.pages = []
            for page in macros("pages", []):
                if "image" not in page:
                    continue
                if not os.path.isfile("input" + page["image"]):
                    print "warning: bad image path in %s: %s" % (page.fname, page["image"])
                    continue
                cls.pages.append(page)
        return cls.pages

    @classmethod
    def all_sorted(cls):
        return sorted(cls.all(), key=lambda p: p.get("date"), reverse=True)

    @classmethod
    def sibling(cls, page):
        all = cls.all_sorted()

        prev = next = None

        for idx, photo in enumerate(all):
            if photo.fname == page.fname:
                next = idx - 1
                prev = idx + 1
                break

        pick = lambda idx: all[idx] if idx >= 0 and idx < len(all) else None
        return pick(prev), pick(next)


def find_jpeg_files(root):
    """Returns all JPEG files in the specified folder"""
    pattern = re.compile(macros("PHOTO_INCLUDE_PATTERN"))

    for folder, folders, files in os.walk(root):
        for file in files:
            fullpath = os.path.join(folder, file)
            shortpath = fullpath[len(root):].lstrip(os.path.sep)

            if not pattern.match(shortpath):
                continue

            yield fullpath


def get_file_description(filename):
    """Gets file title and description from the corresponding .txt file"""
    page_title = os.path.basename(filename)
    page_desc = ""

    descname = os.path.splitext(filename)[0] + ".txt"
    if os.path.exists(descname):
        desc = file(descname, "rb").read().decode("utf-8")
        if "\n---\n" in desc:
            page_title, page_desc = desc.split("\n---\n", 1)
        else:
            page_title = desc

    page_desc = markdown.Markdown().convert(page_desc)

    return page_title.strip(), page_desc.strip()


def get_image_date(filename):
    """Reads original image date from EXIF"""
    img = Image.open(filename)

    exif = img._getexif()
    if exif is not None and 36867 in exif:
        date_original = exif.get(36867)  # DateTimeOriginal

        d, t = date_original.split(" ", 1)
        d = d.replace(":", "-")

        return "%s %s" % (d, t)

    return "0000-00-00 00:00:00"

    ts = os.stat(filename).st_mtime
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def create_photo_page(filename, template):
    """Creates a virtual page for the specified file"""
    img = Image.open(filename)

    image_path = filename.split("/", 1)[1]
    page_name = os.path.splitext(image_path)[0] + ".md"

    page_title, page_desc = get_file_description(filename)
    page_date = get_image_date(filename)
    page_labels = "photo"

    for tag in re.findall("#\w+", page_title):
        page_labels += ", %s" % tag[1:]
    page_title = re.sub("\s*#\w+", "", page_title)

    page = macros("Page")(page_name.decode("utf-8"),
        virtual=template,
        labels=page_labels,
        title=page_title,
        description=page_desc,
        date=page_date,
        image="/" + image_path,
        width=img.size[0],
        height=img.size[1],
        header_anchors="no",
        para_anchors="no")

    return page


def hook_page_contents_photo(page):
    """Returns the photo page contents as a schema.org marked up image."""
    return show_photo(page)


def hook_preconvert_add_images():
    """Finds images named as pages and adds the image property."""
    exts = (".jpg", ".jpeg", ".png")

    for page in macros("pages"):
        if "image" in page:
            continue

        if not page.fname.startswith("./input/"):
            print("warning: unsupported page path: {0}, can't embed images.".format(page.fname))
            return

        img_web_path = None
        img_real_path = None

        fname = os.path.splitext(page.fname)[0]
        for ext in exts:
            _img_name = fname + ext
            if os.path.exists(_img_name):
                if isinstance(_img_name, unicode):
                    _img_name = _img_name.encode("utf-8")
                img_web_path = _img_name[7:]
                img_real_path = _img_name
                break

        if not img_web_path:
            continue  # no related image

        page["image"] = img_web_path
        # print("debug  : picked up {0}".format(img_web_path))

        if "date" not in page:
            page["date"] = get_image_date(img_real_path)
            print("warning: added date for {0} ({1}).".format(
                page.fname, page["date"]))

            p = Page(page.fname)
            p["date"] = page["date"]
            p.save()

        if "labels" not in page:
            page["labels"] = "photo"
        else:
            page["labels"] += ", photo"

        page["anchors"] = "no"
        page["para_anchors"] = "no"

        """
        page.source = u"{{ show_photo() }}\n" \
            + page.source + photo_backlinks(page)
        """


def show_photo(page=None):
    """Returns the HTML code to display the current page's image."""
    if page is None:
        page = macros("page")

    if "image" not in page:
        return ""

    prev, next = Photos.sibling(page)
    size, em = _imagehtml(url=page["image"],
        alt=page["title"],
        max_width=600,
        itemprop="contentUrl",
        cc=False,
        prev=prev,
        next=next)

    html = u'<figure itemscope="itemscope" itemtype="http://schema.org/ImageObject">\n'

    html += u'<div id="photo" style="width: %upx; height: %upx">\n' % size
    html += em
    html += u"</div>\n"

    html += u"<div itemprop='description'>%s</div>\n" % page.html

    html += u"</figure>\n"
    html += photo_backlinks(page)

    return html


def _imagehtml(url, max_width=None, max_height=None, cc=False, prev=None, next=None, **attrs):
    # http://www.strehle.de/tim/weblog/archives/2012/05/31/1494
    # http://www.strehle.de/tim/semtest/
    # http://schema.org/ImageObject

    src_path = "input/" + url.lstrip("/")
    if not os.path.exists(src_path):
        print "warning: image %s not found." % url
        return "<!-- image %s not found -->" % url

    try:
        img = Image.open(src_path)
    except Exception, e:
        print "warning: could not open image %s: %s" % (url, e)
        return (0, 0), "<!-- error opening image %s -->" % url

    width, height = img.size

    """
    if max_width and width > max_width:
        k = float(max_width) / float(width)
        width = int(float(width) * k)
        height = int(float(height) * k)
    """

    attrs["width"] = width
    attrs["height"] = height

    if "title" not in attrs and "alt" in attrs:
        attrs["title"] = attrs["alt"]

    if prev or next:
        attrs["usemap"] = "#navmap"
        attrs["hidefocus"] = "true"

    html = u"<img src='%s'" % url.decode("utf-8")
    for k, v in attrs.items():
        html += u" %s='%s'" % (k, v)
    html += u" />"

    if prev or next:
        html += u"\n<map name='navmap'>"
        if prev:
            html += u"\n<area shape='rect' coords='0,0,%u,%u' href='/%s' rel='next' alt='previous' title='Кликните для просмотра предыдущей фотографии'/>" % (width / 2, height, fix_url(prev.url))
        if next:
            html += u"\n<area shape='rect' coords='%u,0,%u,%u' href='/%s' rel='prev' alt='previous' title='Кликните для просмотра следующей фотографии'/>" % (width / 2, width, height, fix_url(next.url))
        html += u"\n</map>"

    if cc:
        html += u"\n<p>Изображение доступно по лицензии <a itemprop='license' " \
            "href='http://creativecommons.org/licenses/by/3.0/'>CC BY 3.0</a>.</p>"

    return img.size, html


def hook_preconvert_embed_images():
    """Adds support for embedding images using the [photo:local/path] syntax"""
    images = {}
    for page in macros("pages"):
        if "image" in page:
            images[page["image"]] = page

    for page in macros("pages"):
        for match in re.finditer("^\[photo:(.+)\]$", page.source, re.M):
            photo_id = match.group(1)

            if os.path.isfile("input/" + photo_id):
                photo_path = "/" + photo_id
                photo_url = "/" + os.path.splitext(photo_id)[0] + ".html"
            elif os.path.isfile("input/photo/" + photo_id):
                photo_path = "/photo/" + photo_id
                photo_url = "/photo/" + os.path.splitext(photo_id)[0] + ".html"
            elif os.path.isfile("input/photo/%s/photo_m.jpg" % photo_id):
                photo_path = "/photo/%s/photo_m.jpg" % photo_id
                photo_url = "/photo/%s/" % photo_id
            else:
                print "warning: unsupported photo id: %s" % photo_id.encode("utf-8")
                continue

            if photo_path in images:
                photo_title = images[photo_path]["title"]
                photo_desc = images[photo_path].source
            else:
                photo_title, photo_desc = get_file_description("input" + photo_path)

            img = Image.open("input" + photo_path)
            width, height = img.size

            html = "<div itemscope='itemscope' itemtype='http://schema.org/ImageObject'>"
            html += "<img src='%s' alt='%s' width='%u' height='%u' itemprop='contentUrl'/>" \
                % (photo_path, photo_title, width, height)
            html += "</div>"

            if photo_title == os.path.basename(photo_path):
                pass  # print "warning: please create input%stxt" % photo_path[:-3]

            if photo_url != page.url:
                html = "<a href='%s'>%s</a>" % (photo_url, html)

            page.source = page.source.replace(match.group(0), html)


def photo_album(split_months=False, size=75, limit=None, columns=10, label="photo"):
    tiles = {}

    for page in Photos.all_sorted():
        if "date" not in page:
            continue

        labels = get_page_labels(page)
        if "draft" in labels:
            continue
        if label not in labels:
            continue

        if split_months:
            date = get_page_date(page, "%Y/%m")
        else:
            date = "recent"

        if date not in tiles:
            tiles[date] = []

        tiles[date].append({
            "link": page.url,
            "image": "input/" + page["image"].lstrip("/"),
            "fname": page.fname,
            "title": page["title"],
        })

    tiles = sorted(tiles.items(), key=lambda t: t[0], reverse=True)
    return Tiles(tiles, thumbnail_size=(size, size)).render(
        columns=columns, limit=limit, css_class="tiles_photo",
        show_title=False)


def make_thumbnail(src, size, tpl_vars=None, path=False):
    t = Thumbnail(src, width=size, height=size)
    dst = macros("output") + "/" + t.web_path

    if path:
        return dst[6:]

    if tpl_vars is None:
        tpl_vars = {}
    tpl_vars["img_uri"] = dst[6:].decode("utf-8")
    tpl_vars["width"] = size
    tpl_vars["height"] = size
    tpl_vars["large"] = src[5:].decode("utf-8")

    return PHOTO_THUMBNAIL_TEMPLATE % tpl_vars


def page_thumbnail(page, size=75, current_month=None, album="default"):
    image_name = page["image"]
    image_path = "input" + image_name
    thumbnail = make_thumbnail(image_path, size, path=True)
    return thumbnail


def photo_thumbnail(url, size=75, current_month=None):
    album = macros("page").url

    for page in macros("pages"):
        if page.url == url:
            image_name = page["image"]
            image_path = "input" + image_name

            thumbnail = make_thumbnail(image_path, size, {
                "link": fix_url(page.url),
                "title": page.title,
                "album_id": album + "/" + str(current_month),
            })

            return thumbnail

    return "photo %s not found" % url


def photo_nav(count=5):
    matching = []
    current_idx = None
    current_url = macros("page").url

    suspect = filter(lambda p: "date" in p, macros("pages"))
    for p in sorted(suspect, key=lambda p: p["date"]):
        if p.url.startswith("photo/"):
            if current_url == p.url:
                current_idx = len(matching)
            matching.append(p)

    if current_idx is None:
        return ""

    split_at = current_idx - 2
    if split_at > len(matching) - count:
        split_at = len(matching) - count
    if split_at < 0:
        split_at = 0

    matching = matching[split_at:split_at + count]

    output = u"<ul class='photonav'>"
    for p in matching:
        cls = "current" if p.url == current_url else "other"
        try:
            output += u"<li class='%s'><a href='/%s' title='%s'><img src='%s' alt='%s'/></a></li>" \
                % (cls, fix_url(p.url), p["title"], page_thumbnail(p), p["title"])
        except Exception, e:
            print "warning: could not build a thumbnail for %s: %s" % (p.url, e)
    output += u"</ul>"

    return output


def photo_backlinks(page=None):
    if page is None:
        page = macros("page")

    backlinks = []

    img_name = page.get("image").decode("utf-8")
    for p in macros("pages"):
        if "draft" in p.get("labels", ""):
            continue
        if not p.get("title"):
            continue
        if img_name in p.source:
            backlinks.append(p)

    if not backlinks:
        return ""

    output = u"<div id='backlinks'>"
    output += u"<p>Это изображение используется на страницах:</p>"
    output += u"<ul>\n"
    for p in backlinks:
        output += u"<li><a href='/%s'>%s</a></li>\n" % (fix_url(p.url), p["title"])
    output += u"</ul></div>"

    return output


__all__ = [
    "PHOTO_INCLUDE_PATTERN",
    "PHOTO_THUMBNAIL_FOLDER",
    "hook_page_contents_photo",
    "hook_preconvert_add_images",
    "hook_preconvert_embed_images",
    "photo_album",
    "photo_backlinks",
    "photo_nav",
    "photo_thumbnail",
    "show_photo",
]
