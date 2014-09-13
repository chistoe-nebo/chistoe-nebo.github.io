# encoding=utf-8

"""Simple video album plugin for Poole.

Renders previews of posts tagged with the "video" label.
"""


import fnmatch
import sys

from plugins import macros, get_page_date, get_page_labels, \
    fix_url, safedict, Thumbnail, Tiles, get_page_image_path


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"
__version__ = "1.0"


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


def video_album(label=None, columns=3, years=False):
    """Renders a list of all videos.
    
    Videos are pages filtered by label or path (a glob)."""

    tiles = {}

    for video in find_videos(label):
        if not video.get("thumbnail"):
            print "warning: video %s has no thumbnail, example: <http://i.ytimg.com/vi/%s/mqdefault.jpg>" % (video.fname, video["youtube-id"])
            continue

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
            "image": get_page_image_path(video),
            "description": description,
        })

    tiles = sorted(tiles.items(),
        key=lambda t: t[0], reverse=True)
    return Tiles(tiles).render(columns=columns,
        css_class="tiles_video")


def youtube(video_id, link=True):
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
    "youtube",
]
