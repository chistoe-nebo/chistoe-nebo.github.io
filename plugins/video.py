# encoding=utf-8

"""Simple video album plugin for Poole.

Renders previews of posts tagged with the "video" label.
"""


import fnmatch
import lxml.etree
import os
import subprocess
import sys

from plugins import macros, get_page_date, get_page_labels, \
    fix_url, safedict, Thumbnail, Tiles, get_page_image_path, \
    fetch, join_path


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"
__version__ = "1.0"


def add_file_from_url(url, dst):
    print "wraning: fetching %s" % url

    res = fetch(url)
    if res.getcode() < 200 or res.getcode() >= 300:
        print "warning: bad response: %s" % res.getcode()
        return False

    with open(dst, "wb") as f:
        f.write(res.read())

    print "info   : wrote %s" % dst

    p = subprocess.Popen(["hg", "add", dst],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = p.communicate()

    if p.returncode == 0:
        print "info   : added %s to the repository, please commmit" % dst
    else:
        print "warning: could not add %s to the repository" % dst

    return True


def find_videos(label):
    """Finds all video pages, returns a list."""
    if label is None:
        label = "video"

    videos = []
    for page in macros("pages"):
        labels = get_page_labels(page)
        if "draft" in labels:
            continue

        if label not in labels:
            continue

        videos.append(page)

    return sorted(videos, key=lambda p: p.get("date"), reverse=True)


def get_youtube_thumbnail_url(video_id):
    url = "https://gdata.youtube.com/feeds/api/videos/%s" % video_id

    print "warning: fetching %s" % url
    xml = fetch(url).read()

    doc = lxml.etree.fromstring(xml)
    for child in doc.getchildren():
        if child.tag == "{http://search.yahoo.com/mrss/}group":
            thumbnails = []

            for child2 in child.getchildren():
                if child2.tag == "{http://search.yahoo.com/mrss/}thumbnail":
                    turl = child2.get("url")
                    tw = int(child2.get("width"))
                    th = int(child2.get("height"))

                    thumbnails.append((turl, tw * th))

            if thumbnails:
                thumbnails.sort(key=lambda x: x[1], reverse=True)
                return thumbnails[0][0]

    return None


def get_video_thumbnail(page):
    path = os.path.splitext(page.fname)[0] + ".jpg"
    if os.path.exists(path):
        return path

    youtube_id = page.get("youtube-id")
    if youtube_id:
        url = get_youtube_thumbnail_url(youtube_id)
        if url is not None:
            add_file_from_url(url, path)

    return path


def video_album(label=None, columns=3, years=False, size=None):
    """
    Renders a list of all videos.

    Videos are pages filtered by label or path (a glob).
    """

    tiles = {}

    for video in find_videos(label):
        thumbnail = get_video_thumbnail(video)
        if not thumbnail:
            print "warning: page %s has no thumbnail." % video.fname
            contiune

        if years:
            bucket = u"%s год" % get_page_date(video, "%Y")
        else:
            bucket = 0

        if bucket not in tiles:
            tiles[bucket] = []

        description = u""
        if video.get("youtube-views"):
            description = u"%s просмотр(ов)" % video["youtube-views"]

        tiles[bucket].append({
            "link": video.url,
            "title": video["title"],
            "image": thumbnail,
            "description": description,
        })

    if size is None:
        size = (300, 200)

    tiles = sorted(tiles.items(),
        key=lambda t: t[0], reverse=True)
    return Tiles(tiles, size).render(columns=columns,
        css_class="tiles_video")


def youtube(video_id=None, link=True):
    player = u'http://www.youtube.com/embed/%s?rel=0' % video_id

    base_url = macros("BASE_URL")
    if base_url:
        player += "&origin=%s" % base_url

    html = u'<iframe class="youtube-player" src="%s" width="%u" ' \
        'height="%u"></iframe>\n' % (player, 640, 390)  # 540, 335

    if link:
        html += u"\n[Открыть в YouTube](http://youtu.be/%s)\n" % video_id

    return html


def embed_video():
    page = macros("page")

    if "youtube-id" in page:
        html = youtube(page["youtube-id"], link=False)
    elif "vimeo-id" in page:
        html = vieo(page["vimeo-id"], link=False)

    if page.get("summary"):
        html += u"\n%s\n" % page["summary"]

    options = []
    if "youtube-id" in page:
        options.append(u"[Смотреть в YouTube](http://youtu.be/%s)" % page["youtube-id"])
    if "vimeo-id" in page:
        options.append(u"[Смотреть в Vimeo](http://vimeo.com/%s)" % page["vimeo-id"])

    if options:
        html += u"\n\n" + u" &middot; ".join(options)

    return html


__all__ = [
    "video_album",
    "embed_video",
    "find_videos",
    "youtube",
]
