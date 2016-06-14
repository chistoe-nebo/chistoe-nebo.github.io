# encoding=utf-8
# vim: set tw=0:

"""Plugins for Poole

Each module in this package is a self-contained plugin, which starts working as
soon as its contents is imported in macros.py, like this:

    from plugins.meta import *

Some plugins require configuration.  To find out how to do that, either read
the plugin script, or look for warnings during the build process.
"""


import hashlib
from PIL import Image
from PIL import ImageFilter
import os
import re
import shutil
import sys
import time
import urllib
import urlparse

from thumbnails import Thumbnail
from util import *


def fetch(url):
    res = urllib.urlopen(url)
    return res


def get_abs_url(rel_url):
    return urlparse.urljoin(
        macros("BASE_URL", "http://example.com"),
        rel_url)


def is_older(wanted, source):
    if not os.path.exists(wanted):
        return False

    if os.stat(wanted).st_mtime < os.stat(source).st_mtime:
        return False

    return True


def macros(k, v=None):
    """Access properties of the macros module, e.g. pages, or page."""
    return getattr(sys.modules["macros"], k, v)


def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print "info   : created folder %s" % path


def utf(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return s


def join_path(src, dst):
    if "://" in dst:
        return dst

    src = src.split("/")
    src.pop()

    for part in dst.split("/"):
        if part == "":
            src = ["input"]
        elif part == "..":
            src.pop()
        else:
            src.append(part)

    return "/".join(src)


class safedict(object):
    def __init__(self, p):
        self.p = dict(p)

    def __getitem__(self, key):
        return self.p.get(key, "")

    def __setitem__(self, key, value):
        self.p[key] = value


def fix_url_unicode(url):
    output = ""
    for char in url:
        if ord(char) >= 128:
            char = urllib.quote(char.encode("utf-8"))
        output += char
    return output


def fix_url(url):
    """Removes /index.html from local links."""
    if "://" in url:
        return url
    if url.endswith("/index.html"):
        url = url[:-10]
    elif url == "index.html":
        url = ""
    return fix_url_unicode(url)


def get_page_headers(page):
    raw_data = open(page.fname, "rb").read().decode("utf-8")

    headers = []
    for line in raw_data.splitlines():
        if line.startswith("#"):
            continue

        if ":" in line:
            k, v = line.split(":", 1)
            headers.append((k.strip(), v.strip()))

        elif line.strip() == "---":
            break

    return headers


def get_page_url(page):
    """Returns the page's fully-qualified URL."""
    url = fix_url(page["url"])

    base_url = macros("BASE_URL")
    if base_url is not None:
        url = base_url + "/" + url

    return url


def get_page_labels(page):
    """
    Returns a list of page's labels read from the "labels" property.
    The result is cached, next calls are fast.
    """
    if "_parsed_labels" not in page or True:
        _raw_labels = page.get("labels", "").strip()
        if not _raw_labels:
            page["_parsed_labels"] = []
        else:
            page["_parsed_labels"] = re.split(",\s+", _raw_labels)
    return page["_parsed_labels"]


def get_page_date(page, fmt=None):
    if "date" not in page:
        return ""

    if "_parsed_date" not in page:
        default = "0000-00-00 00:00"
        date = (page["date"] + default[len(page["date"]):])[:len(default)]

        try:
            page["_parsed_date"] = time.strptime(date, "%Y-%m-%d %H:%M")
        except ValueError, e:
            print "error  : bad date %s in page %s" % (page["date"], page["fname"])
            return ""

    if not fmt:
        return page["_parsed_date"]

    return time.strftime(fmt, page["_parsed_date"])


def html_body_attrs():
    """Returns a string which adds page-specific classes to an HTML node."""
    page = macros("page")

    classes = page.get_labels()
    classes.append(re.sub("[-./]", "_", page["url"]).replace("_index_html", ""))

    if "body_class" in page:
        classes.append(page["body_class"])

    for k, v in page.items():
        if k.startswith("_"):
            continue
        classes.append("has_" + k.replace("-", "_"))

    return u" class='%s'" % " ".join(list(set(classes)))


def get_page_image_path(page, image=None):
    if "image" in page:
        image = page["image"]
    elif "thumbnail" in page:
        image = page["thumbnail"]
    elif "poster" in page:
        image = page["poster"]
    else:
        image = "_thumbnail.jpg"

    image_path = join_path(page.fname, image)
    if not os.path.exists(image_path):
        raise RuntimeError("source file %s not found, refered in %s." % (image_path, page.fname))

    return image_path


class Page(object):
    def __init__(self, filename):
        self.filename = filename
        self.headers, self.body = self._parse(filename)

    def __getitem__(self, header):
        for k, v in self.headers:
            if k == header:
                return v
        return None

    def __setitem__(self, k, v):
        new_headers = []

        for _k, _v in self.headers:
            if k == _k:
                if v is None:
                    continue
                _v = v
                v = None
            new_headers.append((_k, _v))

        if v is not None:
            new_headers.append((k, v))

        self.headers = new_headers

    def __repr__(self):
        return "<Page %s>" % self.filename

    def _parse(self, filename):
        with open(filename, "r") as f:
            raw_page = f.read().decode("utf-8")

        if u"\n---\n" in raw_page:
            head, body = raw_page.split("\n---\n")
        else:
            head = None
            body = raw_page

        if head is None:
            headers = []
        else:
            headers = [re.split("\s*:\s*", l, 1)
                for l in head.split("\n")
                if l.strip()]

        return headers, body

    def save(self):
        backup = self.filename + "~"

        if os.path.exists(self.filename):
            if os.path.exists(backup):
                os.unlink(backup)
            os.rename(self.filename, backup)

        with open(self.filename, "wb") as f:
            for k, v in self.headers:
                f.write("%s: %s\n" % (k.encode("utf-8"), unicode(v).encode("utf-8")))
            f.write("---\n")
            f.write(self.body.encode("utf-8"))


class Tiles(object):
    def __init__(self, items, thumbnail_size=None):
        self.items = items
        self.thumbnail_size = thumbnail_size or (300, 200)

    def render(self, columns=3, css_class=None, limit=None, show_title=True):
        output = u""

        cls = "tiles tiles_{0}x{1} tiles_{2}col".format(
            self.thumbnail_size[0], self.thumbnail_size[1],
            columns)
        if css_class:
            cls += " " + css_class

        for name, items in self.items:
            if len(self.items) > 1:
                output += u"<h2>%s</h2>\n" % name

            _limit = limit or len(items)

            output += u"<ul class='%s'>\n" % cls
            for idx, tile in enumerate(items[:_limit]):
                link = fix_url(tile["link"]) if "link" in tile else None
                title = tile.get("title")

                if "image" in tile:
                    t = Thumbnail(tile["image"],
                        width=self.thumbnail_size[0],
                        height=self.thumbnail_size[1])
                elif "://" in tile.get("image_url"):
                    t = Thumbnail.from_url(tile["image_url"],
                        width=self.thumbnail_size[0],
                        height=self.thumbnail_size[1])
                elif "image_url" in tile:
                    fn = urlparse.urljoin(
                        tile["link"], tile["image_url"])
                    t = Thumbnail.from_file(
                        os.path.join("input", fn),
                        width=self.thumbnail_size[0],
                        height=self.thumbnail_size[1])
                else:
                    raise ValueError("a tile lacks image/image_url.")

                image = t.get_url()

                item_class = "col{0}".format(idx % columns)
                if idx == 0:
                    item_class += " col_first"
                elif (idx % columns) == (columns - 1):
                    item_class += " col_last"
                else:
                    item_class += " col_mid"

                output += u"<li class='{0}' itemscope='itemscope' " \
                          u"itemtype='http://schema.org/ImageObject'>".format(item_class)

                img = u"<img itemprop='contentUrl' src='%s' alt='%s' class='picture'/>" % (image, title or "thumbnail")

                if link:
                    if "://" not in link and not link.startswith("/"):
                        link = "/" + link
                    a = u"<a href='%s'" % link
                    if title:
                        a += u" title='%s'" % title
                    if link.endswith(".jpg"):
                        a += u" data-lightbox='gallery'"
                        if title:
                            a += u" data-title='%s'" % title

                    output += a + u">" + img + u"</a>"

                image_url = self.get_image_url(tile)
                if image_url:
                    output += u"<meta itemprop='contentUrl' content='%s'/>" % image_url

                if tile.get("pre_title"):
                    output += tile["pre_title"]

                if not show_title:
                    title = None

                if title or tile.get("text"):
                    desc = u""
                    if title:
                        desc += u"<span class='title' itemprop='name'>%s.</span>" % title
                    if tile.get("description"):
                        desc += u"<span class='caption' itemprop='caption'>%s</span>" % tile["description"]
                    output += u"<div class='description'>%s</div>" % desc

                output += u"</li>"

            output += u"</ul>\n"

        return output

    def get_image_url(self, tile):
        base_url = macros("BASE_URL")
        if not base_url:
            return None

        if not tile.get("link"):
            return None

        page_url = urlparse.urljoin(base_url, tile["link"])

        image = tile["image"]
        if image.startswith("input/"):
            image = image[5:]
        elif image.startswith("./input/"):
            image = image[7:]

        image_url = urlparse.urljoin(page_url, image)
        return image_url


def find_sibling(pages, current):
    prev = next = last = None

    for page in pages:
        if page.fname == current.fname:
            prev = last

        elif last and last.fname == current.fname:
            next = page

        last = page

    return prev, next


def element(name, attrs, contents=None):
    html = u"<%s" % name

    deutf = lambda s: unicode(s, "utf-8") if isinstance(s, str) else unicode(s)

    for k, v in sorted(attrs.items()):
        if v:
            html += u" %s=\"%s\"" % (k, deutf(v))

    if contents:
        html += u">%s</%s>" % (deutf(contents), name)
    else:
        html += u" />"

    return html


__all__ = [
    "find_sibling",
    "fix_url",
    "fix_url_unicode",
    "get_page_headers",
    "get_abs_url",
    "get_page_date",
    "get_page_image_path",
    "get_page_labels",
    "get_page_url",
    "join_path",
    "html_body_attrs",
    "macros",
    "Page",
    "safedict",
    "Tiles",
]
