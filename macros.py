# vim: set fileencoding=utf-8 tw=0 nofoldenable:

import cgi
import csv
import glob
import hashlib
import imp
import os
import re
import shutil
import sys
import time


BASE_URL = "http://www.chistoe-nebo.info"
WEBSITE_NAME = u"Поселение Чистое небо"
DEFAULT_LANGUAGE = "ru"
STOP_LABELS = ["draft", "status", "link", "queue"]

from plugins import *

from plugins.disqus import *
DISQUS_ID = "chistoenebo"

from plugins.simple_menu import *
#SIMPLE_MENU_FIXED = [("volunteer/", u"Волонтёрам", None, 60, None)]

from plugins.sitemap import *
SITEMAP_BLACKLIST_IMAGES = "^/thumbnails/"

from plugins.meta import *
OG_COUNTRY_NAME = "Russia"
OG_LOCALITY = "Sebezh"
OG_EMAIL = "hex@umonkey.net"
OG_DEFAULT_IMAGE = "http://www.chistoe-nebo.info/images/opengraph.png"

from plugins.typo import *

from plugins.yandex_metrika import *
YANDEX_METRIKA_ID = "27824553"

#from plugins.photopages import *
#PHOTO_PAGE_TEMPLATE = "photo_template.md"
#PHOTO_INCLUDE_PATTERN = "^photo/[^/]+\.jpg$"

#from plugins.podcast import *

#from plugins.shadowbox import *

#from plugins.feeds import *
#from plugins.pagelist import *

#from plugins.pagemeta import *
#PAGEMETA_LABELS = ["blog", "photo", "animals"]

#from plugins.anchors import *
#ANCHOR_SYMBOL = u"⚓"

#from plugins.authors import *
#AUTHORS = [{
#    "name": "umonkey",
#    "display_name": u"Владимир",
#    "link": "https://plus.google.com/111824683191076754514/posts",
#    "default": True,
#}, {
#    "name": "estel",
#    "display_name": u"Юлия",
#    "link": "http://vk.com/e_stel",
#    "sex": "f",
#}]

from plugins.rdfa import *

from plugins.video import *

#from plugins.microblog import *
MICROBLOG_SOURCE = "input/microblog.txt"
#MICROBLOG_FEED = "output/microblog.xml"
#MICROBLOG_URL = "http://land.umonkey.net/micro/"
MICROBLOG_LANG = "rus"
MICROBLOG_TITLE = u"Микроблог из деревни"
MICROBLOG_DESCRIPTION = u"Ссылки и короткие заметки."
MICROBLOG_STRIP_HASHTAGS = True


page = {}
pages = []


# Place your own Poole hooks here.


def fix_url(url):
    """Removes /index.html from local links."""
    if url.endswith("/index.html"):
        return url[:-10]
    elif url == "index.html":
        return ""
    return url


def gallery(label):
    items = []
    for page in pages:
        if label in get_page_labels(page) and is_page_visible(page):
            html = u"<li><a href='/%s'>" % strip_url(page["url"])
            html += u"<img src='%s' alt='image'/>" % page["image"]
            html += u"<span>%s</span>" % page["title"]
            html += u"</a></li>"
            items.append(html)

    if not items:
        return u"Эта галерея пуста."

    output = u"<ul class='gallery'>\n%s\n</ul>" % u"\n".join(items)
    return output


def wrap_content(contents):
    """Вывод основного содержимого страницы, обрамление добавками.  Для блога
    добавляется предложение подписаться на RSS, например."""
    labels = get_page_labels(page)

    html = u""

    hook_names = [f for f in globals()
        if f.startswith("hook_page_contents_")]
    hooks = [getattr(sys.modules["macros"], f)
        for f in sorted(hook_names)]

    for hook in hooks:
        value = hook(page)
        if value is not None:
            html += value
            break

    if not html:
        html += page.html

    return html


def static_file_url(filename):
    """Returns a link to the specified file.  The link contains a string that
    prevents caching the file after it's changed (technically it adds an MD5
    hash of the contents)."""

    import hashlib

    path = os.path.join("input", filename)
    if not os.path.exists(path):
        return path

    contents = file(path, "rb").read()
    checksum = hashlib.md5(contents).hexdigest()

    return filename + "?hash=" + checksum


def get_page_icons(page):
    icons = page.get("icons")
    if not icons:
        return None

    titles = {
        "home": u"размещение в доме",
        "tents": u"размещение в палатке",
        "sauna": u"баня",
        "boat": u"выход к озеру",
        "kids": u"есть дети (не грудные)",
        "bicycle": u"велосипед в аренду",
        "wifi": u"бесплатный wifi",
    }

    parts = []
    for icon in re.split(",\s+", icons):
        path = "input/images/icons/%s.png" % icon
        if not os.path.exists(path):
            print "warning: bad icon %s for page %s" % (icon, page.fname)
            continue

        src = "/images/icons/%s.png" % icon
        parts.append("<img src='%s' alt='%s' title='%s'/>" % (src, icon, titles.get(icon, icon)))

    if not parts:
        return None

    return "<div class=\"icons\">%s</div>" % "".join(parts)


def tiles_by_pattern(pattern, columns=3, sort="title", reverse=False, limit=None):
    """Вывод картинок с животными."""
    from plugins import Tiles
    from fnmatch import fnmatch

    tiles = []

    for page in sorted(pages, key=lambda p: p.get(sort), reverse=reverse):
        if page.get("hidden") == "yes":
            continue

        labels = get_page_labels(page)

        if "draft" in labels:
            continue

        if not fnmatch(page.url, pattern):
            continue

        image = get_page_image_path(page)
        if not image:
            print "warning: page %s has no image or thumbnail, hidden." % page.fname
            continue

        tiles.append({
            "link": page.url,
            "title": page.get("list_title", page["title"]),
            "pre_title": get_page_icons(page),
            "description": page.get("list_text"),
            "image": image,
        })

    if not tiles:
        print "warning: nothing to show on page %s" % macros("page").fname
        return ""

    if limit:
        tiles = tiles[:limit]

    return Tiles([(None, tiles)], (326, 233)).render()


def video_album4(label):
    return video_album(label=label, columns=4, size=(240, 160))


def album(desc, columns=3, sizes=None):
    if isinstance(desc, unicode):
        desc = desc.encode("utf-8")
    elif not isinstance(desc, str):
        print "error  : bad album format in %s, must be: image[;link[;title[;desc]]]" % page.fname
        return "<!-- bad album format -->"

    if sizes is not None:
        pass
    elif columns == 4:
        sizes = (240, 160)
    else:
        sizes = (326, 233)

    tiles = []

    lines = [l for l in desc.splitlines() if l.strip()]
    reader = csv.reader(lines, delimiter=";")

    deutf = lambda s: s.decode("utf-8") if isinstance(s, str) else s

    for parts in reader:
        while len(parts) < 4:
            parts.append(None)

        image = join_path(page.fname, parts[0]) if parts[0] else None
        link = join_path(page.url, parts[1]) if parts[1] else image[7:]
        title = parts[2]
        desc = parts[3]

        tiles.append({
            "image": image,
            "link": link,
            "title": deutf(title),
            "description": deutf(desc),
        })

    return Tiles([(None, tiles)], sizes).render(
        css_class="album", columns=columns)


def album4(tiles):
    return album(tiles, columns=4)


def format_pagelist_title(page):
    """Форматирование ссылки на пост в списке"""
    page_url = fix_url(page["url"])

    labels = get_page_labels(page)
    cls = "flag" if "flag" in labels else "noflag"

    return u"<a class='%s' href='/%s'>%s</a>" % (cls, page_url, cgi.escape(page["title"]))


def format_feed_item_title(page):
    title = page["title"]
    if title.startswith(u"Подкаст №"):
        title = u"Подкаст из экопоселения: эпизод %s" % title.split(" ", 1)[1]
    return title


def page_title():
    title = page.get("title")
    labels = get_page_labels(page)

    if "animals" in labels:
        _t = title[0].lower() + title[1:]
        title = u"<a href='/nature/'>Природа</a>: %s" % _t
    elif "video" in labels:
        _t = title[0].lower() + title[1:]
        title = u"<a href='/video/'>Видеозаписи</a>: %s" % _t
    elif "title_html" in page:
        title = page["title_html"]
    elif "stay" in labels:
        _t = title[0].lower() + title[1:]
        title = u"<a href='/stay/'>Размещение</a>: %s" % _t
    elif "residents" in labels and page.url != "residents/index.html":
        _t = title[0].lower() + title[1:]
        title = u"<a href='/residents/'>Поселенцы</a>: %s" % _t

    return title


def wide_image():
    img = page.get("wideimage")
    if not img:
        return ""

    img = join_path(page.url, img)

    if page.get("widetext"):
        html = u"<div class='wide'>"
        html += u"<div class='image' style='background-image:url(/%s)'></div>" % img
        html += u"<div class='text'>"
        html += u"<h1>%s</h1>" % page["title"]
        html += u"<p>%s</p>" % page["widetext"]
        html += u"</div>"
    else:
        html = u"<div class='wide' style='background-image:url(/%s)'>" % img

    html += u"</div>\n"

    return html


def strip_ws(html):
    html = re.sub(r"</div>\s+<", "</div><", html, re.M)
    return html


def include(path):
    base = os.path.dirname(page.fname)
    real = os.path.abspath(os.path.join(base, path))
    if os.path.exists(real):
        return strip_ws(open(real, "rb").read().decode("utf-8"))
    else:
        return "<!-- file %s not found -->" % path


def get_video_nav(page):
    videos = find_videos("video")
    videos.sort(key=lambda p: p["date"])
    prev, next = find_sibling(videos, page)

    if not prev and not next:
        return None

    parts = []
    if prev:
        parts.append(u"<a href='/%s' class='prev' title='%s'>Предыдущее видео</a>" % (prev.url, prev.title))
    if next:
        parts.append(u"<a href='/%s' class='next' title='%s'>Следущее видео</a>" % (next.url, next.title))
    return "".join(parts)


def embed_video():
    if "youtube-id" in page:
        vhtml = youtube(page["youtube-id"], link=False)
    elif "vimeo-id" in page:
        vhtml = vieo(page["vimeo-id"], link=False)

    lines = []
    if "summary" in page:
        lines.append("<p class='summary'>%s</p>" % page["summary"])
    if "date" in page:
        lines.append("<p class='date'>%s</p>" % page["date"])

    html = u"<div class='row'>"
    html += u"<div class='col'>%s</div>" % vhtml
    if lines:
        html += u"<div class='col'>%s</div>" % "".join(lines)
    html += u"</div>"

    nav_html = get_video_nav(page)
    if nav_html:
        html += u"<div class='nav'>%s</div>" % nav_html

    return html


def find_residents():
    label = "residents"
    residents = [p for p in pages
                 if label in get_page_labels(p)
                 and p.get("hidden") != "yes"]
    residents.sort(key=lambda p: p["title"].lower())
    return residents


def hook_postconvert_other_residents():
    residents = find_residents()

    for page in pages:
        if "residents" not in get_page_labels(page):
            continue

        tiles = [{
            "image": join_path(res.fname, res["thumbnail"]),
            "link": res.url,
            "title": res["title"],
        } for res in residents
          if res.fname != page.fname]

        if not tiles:
            continue

        tiles_html = Tiles([(None, tiles)], (75, 75)).render(
                           css_class="other_residents",
                           columns=100)

        bonus = u"<div class='other'>"
        bonus += u"<h3>Познакомьтесь и с другими нашими жителями:</h3>"
        bonus += tiles_html
        bonus += u"</div>"

        page.html += bonus


def meta(key):
    if key not in page:
        print "warning: page %s has no meta header '%s'" % (page.fname, key)
    else:
        return page[key]


def hook_html_99_minify(html):
    html = re.sub(r"^\s+", "", html, count=0, flags=re.M)
    html = re.sub(r"<!--.*?-->", "", html)
    return html


def find_files(root, suffix=None):
    result = []
    for folder, folders, files in os.walk(root):
        for file in files:
            if suffix is None or file.endswith(suffix):
                result.append(os.path.join(folder, file))
    return sorted(result)


def compress_files(files):
    source = ""
    for file in files:
        if file.endswith(".js"):
            source += ";"
        source += open(file, "rb").read()

    length = len(source)

    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"^\s+", "", source, flags=re.M)

    lines = source.splitlines()
    lines = [l for l in lines if l.strip()]
    source = "\n".join(lines)

    return length, source


def hook_after_00_compress_css():
    sources = find_files("css.d", ".css")
    length, source = compress_files(sources)

    filename = os.path.join(output, "assets", "screen.css")
    with open(filename, "wb") as f:
        saved = length - len(source)
        f.write(source)
        print "info   : wrote assets/screen.css (compressed, %u bytes saved)" % saved


def hook_after_00_compress_js():
    sources = []

    for target in os.listdir("js.d"):
        root = os.path.join("js.d", target)
        sources = find_files(root, ".js")
        length, source = compress_files(sources)

        filename = os.path.join(output, "assets", target)
        with open(filename, "wb") as f:
            saved = length - len(source)
            f.write(source)
            print "info   : wrote assets/%s (compressed, %u bytes saved)" % (target, saved)


def page_scripts():
    if "script" not in page:
        return ""

    output = u""
    for k, v in get_page_headers(page):
        if k == "script":
            output += u"<script type='text/javascript' src='%s'></script>\n" % v
        elif k == "style":
            output += u"<link rel='stylesheet' type='text/css' href='%s'/>\n" % v

    return output


def is_page_commentable(page):
    if page.get("comments") != "yes":
        return False

    if "draft" in get_page_labels(page):
        return False

    return True


def prepare_square_photos():
    """
    Создание квадратных превьюшек для фотографий на главной.

    Создаются автоматически, если файла нет.  Можно заменить файл ручной версией.
    """
    pattern = "input/photo/*.jpg"

    for src in glob.glob(pattern):
        if src.endswith(".sq.jpg"):
            continue

        name, ext = os.path.splitext(src)
        dst = name + ".sq.jpg"

        if not os.path.exists(dst):
            tn = Thumbnail(src, width=75, height=75, fit=True)
            shutil.copy(tn.tmp_path, dst)
            print "info   : created %s" % dst


prepare_square_photos()
