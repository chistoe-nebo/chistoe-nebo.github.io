# encoding=utf-8

"""Sitemap plugin for Poole

This plugin generates a sitemap.xml for your website.  To enable it, load the
script and specify the file name, like this:

    from plugins.sitemap import *

Use SITEMAP_NAME to override the output file name, defaults to "sitemap.xml".
This name will be added to robots.txt.

Use STOP_LABELS to set a list of labels which prevent pages from being listed
in the sitemap.

Use SITEMAP_EXTRA_URLS to add URLs which aren't pages, e.g. plain HTML pages,
example: SITEMAP_EXTRA_URLS = ['volunteer/']

Implements the image sitemap protocol,
http://www.google.com/schemas/sitemap-image/1.1/sitemap-image.xsd
"""

import cgi
import os
import re
import sys
import urllib

import lxml.html

from plugins import macros, get_page_labels


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"


class Sitemap(object):
    def __init__(self):
        self.filename = macros("SITEMAP_NAME", "sitemap.xml")
        self.base_url = macros("BASE_URL")
        self.stop_labels = macros("STOP_LABELS", [])

        tmp = macros("SITEMAP_BLACKLIST_IMAGES", None)
        self.blacklist_images = re.compile(tmp) if tmp else None

        self.find_pages()

    def find_pages(self):
        """Finds pages to list in the sitemap."""
        self.pages = []
        self.images = {}

        for page in macros("pages", []):
            labels = get_page_labels(page)
            if set(labels) & set(self.stop_labels):
                continue

            self.pages.append(page)

            if "image" in page:
                url = self.base_url + page["image"]
                self.images[url] = page

    def find_urls(self):
        result = {}
        for page in self.pages:
            url = get_abs_url(page["url"], self.base_url)
            result[url] = {
                "images": self.find_page_images(page),
                "video": self.find_page_video(page),
            }

        extra = macros("SITEMAP_EXTRA_URLS")
        if isinstance(extra, list):
            for url in extra:
                url = get_abs_url(url, self.base_url)
                result[url] = {"images": [], "video": []}

        return result

    def find_page_images(self, page):
        images = []

        if not page.html:
            return []

        doc = lxml.html.fromstring(page.html)
        for image in doc.xpath("//img"):
            src = image.get("src")
            if self.blacklist_images and self.blacklist_images.match(src):
                continue

            src = image.get("src")
            if not src.startswith("/") and "://" not in src:
                src = u"/" + src

            images.append({
                "src": self.absolute(src),
                "title": image.get("alt"),
                "caption": image.get("data-description"),
                "location": image.get("data-location"),
                "license": image.get("data-license"),
            })

        return images

    def find_page_video(self, page):
        if "youtube-id" in page:
            return {
                "title": page["title"],
                "description": page.get("summary"),
                "thumbnail_loc": "http://i.ytimg.com/vi/%s/mqdefault.jpg" % page["youtube-id"],
                "player_loc": "http://youtube.com/v/" + page["youtube-id"],
                "date": page["date"][:10],
                "duration": page.get("duration"),
            }

    def generate(self):
        xml = "<?xml version='1.0' encoding='UTF-8'?>\n"
        xml += "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9\' \n" \
            " xmlns:image='http://www.google.com/schemas/sitemap-image/1.1'\n" \
            " xmlns:video='http://www.google.com/schemas/sitemap-video/1.1'>"

        quote = lambda s: cgi.escape(s)
        urlencode = lambda s: urllib.quote(s.encode("utf-8"), "/:,")

        for url, items in sorted(self.find_urls().items()):
            xml += "<url>\n"
            xml += "\t<loc>%s</loc>\n" % urlencode(url)

            for image in items["images"]:
                xml += "\t<image:image>\n"
                xml += "\t\t<image:loc>%s</image:loc>\n" % urlencode(image["src"])
                if image["title"]:
                    xml += "\t\t<image:title>%s</image:title>\n" % image["title"]
                if image["caption"]:
                    xml += "\t\t<image:caption>%s</image:caption>\n" % image["caption"]
                if image["location"]:
                    xml += "\t\t<image:geo_location>%s</image:geo_location>\n" % image["location"]
                if image["license"]:
                    xml += "\t\t<image:license>%s</image:license>\n" % image["license"]
                xml += "\t</image:image>\n"

            try:
                if items.get("video"):
                    video = items["video"]
                    xml += "\t<video:video>\n"
                    xml += "\t\t<video:title>%s</video:title>\n" % quote(video["title"])
                    if video.get("description"):
                        xml += "\t\t<video:description>%s</video:description>\n" % quote(video["description"])
                    xml += "\t\t<video:thumbnail_loc>%s</video:thumbnail_loc>\n" % quote(video["thumbnail_loc"])
                    xml += "\t\t<video:player_loc allow_embed='yes' autoplay='ap=1'>%s</video:player_loc>\n" % quote(video["player_loc"])
                    xml += "\t\t<video:publication_date>%s</video:publication_date>\n" % quote(video["date"])
                    if video.get("duration"):
                        xml += "\t\t<video:duration>%s</video:duration>\n" % quote(video["duration"])
                    xml += "\t</video:video>\n"
            except Exception, e:
                print "error  : could not add %s to video sitemap: %s" % (url.encode("utf-8"), e)

            xml += "</url>\n"

        xml += "</urlset>\n"
        return xml

    def absolute(self, url):
        if "://" in url:
            return url
        return self.base_url + url

    def write(self):
        if not self.base_url:
            print >> sys.stderr, "warning: BASE_URL not set in macros.py -- no sitemap for you"
            return

        output = macros("output")

        xml = self.generate()
        file(os.path.join(output, self.filename),
            "wb").write(xml.encode("utf-8"))

        print "info   : wrote %s" % self.filename

        robots = os.path.join(output, "robots.txt")
        file(robots, "ab").write("Sitemap: %s\n" \
            % get_abs_url(self.filename, self.base_url))


def get_abs_url(url, base_url):
    """Returns the page's fully-qualified URL."""
    if base_url is not None:
        url = base_url + "/" + url

    fn = macros("fix_url")
    if fn is not None:
        url = fn(url)

    return url


def hook_postconvert_sitemap():
    Sitemap().write()


__all__ = [
    "hook_postconvert_sitemap",
]
