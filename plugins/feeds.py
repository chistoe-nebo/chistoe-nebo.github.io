# encoding=utf-8

"""RSS export plugin for Poole

This plugin generates RSS feeds.  Each feed is controlled by a file with the
"feed" extension, which looks like this:

    title: My podcast
    description: A podcast about a static website developer's life.
    language: ru-RU
    link: /podcast/
    labels: podcast, audio
    limit: 1000

Title and description are required, other properties are optional.  Laguage
defaults to "en-US"; labels specify one of labels which pages must have to be
listed; limit defaults to 10.

To have a /feeds/podcast.xml feed, write its description in a file named
input/feeds/podcast.feed and rebuild the web site.

Custom item title formatting can be done with a hook:

    def format_feed_item_title(page):
        return page["title"] + u"!"
"""

import cgi
import email.utils
import mimetypes
import os
import re
import sys
import time
import urllib
import urlparse

from plugins import fix_url_unicode, macros
from plugins import utf


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"

files_to_convert = []


def feed_to_xml(src, dst):
    """The fake converter function.  Only stores file names for later use in
    the postconvert hook."""
    global files_to_convert
    files_to_convert.append((src, dst))


def parse_feed_description(src):
    """Reads feed description, returns a dictionary."""
    feed = {
        "limit": 10,
        "language": "en-US",
        "link": "/",
        "description": "No description for this feed.",
        "title": "Untitled feed",
        "with_bodies": "yes",
    }

    data = file(src, "rb").read().decode("utf-8")
    for line in data.rstrip().split("\n"):
        k, v = line.split(":", 1)
        v = v.strip()
        if k == "labels":
            v = re.split(",\s*", v)
        elif k == "limit":
            v = int(v)
        feed[k] = v

    return feed


def page_matches(page, feed):
    if "date" not in page:
        return False

    page_labels = set(re.split(",\s*", page.get("labels", "")))

    stop_labels = macros("STOP_LABELS", [])
    if stop_labels and set(stop_labels) & page_labels:
        return False

    if "labels" in feed and not(set(feed["labels"]) & page_labels):
        return False

    return True


def get_abs_url(url):
    base_url = macros("BASE_URL")
    if base_url is not None:
        url = base_url.rstrip("/") + "/" + url.lstrip("/")

    fix_url = macros("fix_url", lambda s: s)
    url = fix_url(url)

    return url


def format_date(date):
    default = "0000-00-00 00:00:00"
    date = (date + default[len(date):])[:len(default)]

    ts = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    return email.utils.formatdate(time.mktime(ts))


def cleanup_description(html):
    """Removes unnecessary or unrecommended portions of the description."""
    patterns = []

    # Remove anchor pointers (don't work in RSS).
    patterns.append(" id='[^']+' class='with-anchor'")

    # Remove RDFa attributes.
    # TODO: more selective.
    patterns.append("\s+(itemscope|itemtype|itemprop)='[^']*'")
    patterns.append("\s+(itemscope|itemtype|itemprop)=\"[^\"]*\"")

    # Remove videoplayers (there are links).
    patterns.append("<iframe\s.*</iframe>")

    # Remove all unnecessary code.
    for pattern in patterns:
        html = re.sub(pattern, "", html)

    # Fix relative links.
    base = macros("BASE_URL")

    pattern = " (href|src)=['\"]([^'\"]+)['\"]"
    for match in re.finditer(pattern, html):
        old_tag = match.group(0)
        old_link = match.group(2)
        if old_link.startswith("/"):
            new_link = base + old_link
            new_tag = old_tag.replace(old_link, new_link)
            html = html.replace(old_tag, new_tag)

    return html


def get_page_description(page):
    if "image" in page:
        url = urlparse.urljoin(macros("BASE_URL"), page.url)
        url = urlparse.urljoin(url, page["image"])

        html = "<p><img src='%s' alt='attached image'/></p>" % url
        return html + page.html
    else:
        return page.html


def add_podcast(page):
    _url = utf(page["file"])
    _type = "audio/mp3"
    _length = int(page.get("filesize", "0"))

    return "\t<enclosure url='%s' type='%s' length='%u'/>\n" \
        % (_url, _type, _length)


def write_rss(filename, feed, pages):
    """Writes an RSS feed."""
    ux = lambda s: cgi.escape(s.encode("utf-8"))
    urlencode = lambda s: urllib.quote(s.encode("utf-8"), ":/,")
    base = macros("BASE_URL", "")

    title_fmt = macros("format_feed_item_title", lambda p: p["title"])

    xml = "<?xml version='1.0' encoding='UTF-8'?>\n"
    xml += "<rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom' xmlns:itunes='http://www.itunes.com/dtds/podcast-1.0.dtd'>\n"
    xml += "<channel>\n"

    rss_link = base + filename[8:]
    xml += "<atom:link href='%s' rel='self' type='application/rss+xml'/>\n" % ux(rss_link)

    if "language" in feed:
        xml += "<language>%s</language>\n" % ux(feed["language"])
    xml += "<docs>http://blogs.law.harvard.edu/tech/rss</docs>\n"
    xml += "<generator>Poole</generator>\n"

    rss_link = base + "/" + feed["link"].lstrip("/")
    xml += "<link>%s</link>\n" % urlencode(rss_link)

    xml += "<title>%s</title>\n" % ux(feed["title"])
    if feed["with_bodies"] == "yes":
        xml += "<description>%s</description>\n" % ux(feed["description"])

    if "hub" in feed:
        xml += "<atom:link rel='hub' href='%s'/>\n" % ux(feed["hub"])

    show_pages = pages[:feed["limit"]]

    max_date = max([page["date"] for page in show_pages])
    max_date_str = format_date(max_date)
    xml += "<pubDate>%s</pubDate>\n" % max_date_str
    xml += "<lastBuildDate>%s</lastBuildDate>\n" % max_date_str

    for page in show_pages:
        try:
            pub_date = format_date(page["date"])
        except ValueError, e:
            print "error  : bad date %s in page %s" % (page["date"], page.fname)
            continue

        xml += "<item>\n"
        xml += "\t<pubDate>%s</pubDate>\n" % ux(pub_date)
        xml += "\t<title>%s</title>\n" % ux(title_fmt(page))

        description = get_page_description(page)
        xml += "\t<description>%s</description>\n" \
            % ux(cleanup_description(description))

        if page.get("file", "").endswith(".mp3"):
            xml += add_podcast(page)

        elif page.get("image"):
            image_path = "input" + page["image"]
            if not os.path.exists(image_path):
                print "warning: enclosure %s does not exist." % image_path
            else:
                image_link = page["image"]
                if image_link.startswith("/"):
                    image_link = base + image_link

                ct = mimetypes.guess_type(image_link)[0]
                size = os.stat(image_path).st_size

                try:
                    xml += "\t<enclosure url='%s' type='%s' length='%u'/>\n" % (str(image_link), ct, size)
                except Exception, e:
                    print e, image_link, ct, size

        item_link = urlencode(get_abs_url(page["url"]))
        xml += "\t<link>%s?from=rss</link>\n" % item_link
        xml += "\t<guid>%s</guid>\n" % item_link

        xml += "</item>\n"

    xml += "</channel>\n"
    xml += "</rss>\n"

    file(filename, "wb").write(xml)

    print "info   : wrote %s" % filename


def convert_feed(src, dst):
    feed = parse_feed_description(src)

    pages = [p for p in macros("pages", []) if page_matches(p, feed)]
    pages.sort(key=lambda p: p["date"], reverse=True)

    write_rss(dst, feed, pages)


def hook_postconvert_feed_to_xml():
    """Converts all found .feed files to .xml"""
    for src, dst in files_to_convert:
        convert_feed(src, dst)


def install_converters():
    """Installs the .feed -> .xml converter"""
    mod = sys.modules["macros"]

    conv = getattr(mod, "converter", {})
    conv[r"\.feed"] = (feed_to_xml, "xml")
    setattr(mod, "converter", conv)


__all_ = [
    "hook_postconvert_feed_to_xml",
]


if __name__ == "__main__":
    pass
else:
    install_converters()
