# vim: set fileencoding=utf-8 tw=0 nofoldenable:

import cgi
import glob
import hashlib
import imp
import os
import re
import shutil
import sys

BASE_URL = "http://nebo.dev.umonkey.net"
WEBSITE_NAME = u"Поселение Чистое небо"
DEFAULT_LANGUAGE = "ru"
STOP_LABELS = ["draft", "status", "link", "queue"]

from plugins import *

from plugins.simple_menu import *
#SIMPLE_MENU_FIXED = [("volunteer/", u"Волонтёрам", None, 60, None)]

from plugins.sitemap import *
SITEMAP_BLACKLIST_IMAGES = "^/thumbnails/"

from plugins.meta import *
OG_COUNTRY_NAME = "Russia"
OG_LOCALITY = "Sebezh"
OG_EMAIL = "poselenie@chistoe-nebo.net"

#from plugins.yandex_metrika import *
#YANDEX_METRIKA_ID = "14608519"

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

#from plugins.rdfa import *

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


def typo(text):
    text = text.replace(u".  ", u".&nbsp; ")
    return text


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

    html += subscribe_please()
    html += similar_posts()
    return html


def subscribe_please():
    labels = set(re.split(",\s*", page.get("labels", "")))

    if set(["blog", "nature"]) & labels:
        return u"<p>Следить за развитием событий удобнее всего с помощью <a href=\"/blog/subscribe/\">почтовой рассылки</a> или <a href=\"/blog.xml\">RSS ленты</a>.</p>"

    elif "podcast" in labels:
        return u"<p>Следить за развитием событий удобнее всего с помощью <a href=\"/podcast.xml\">RSS ленты</a>, есть <a href='http://farm.rpod.ru/'>зеркало на Russian Podcasting</a>.</p>"

    elif "photo" in labels:
        return u"<p>Следить за нашим <a href='/photo/'>фотоблогом</a> удобнее всего с помощью <a href='/photo.xml'>RSS ленты</a>.</p>"

    else:
        return u""


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


def metrika(filename):
    import json

    months = [u"Январь", u"Февраль", u"Март", u"Апрель", u"Май", u"Июнь",
        u"Июль", u"Август", u"Сентябрь", u"Октябрь", u"Ноябрь", u"Декабрь"]

    def fmt(value):
        if value < 1000:
            return str(value)
        return "%u&nbsp;%03u" % (value / 1000, value % 1000)

    try:
        with open(filename, "rb") as f:
            data = json.loads(f.read())

            output = u"<table id='metrika'>\n"
            output += u"<thead><tr>"
            output += u"<th>Месяц</th>"
            output += u"<th>Посетители</th>"
            output += u"<th>Визиты</th>"
            output += u"<th>Страницы</th>"
            output += u"<th>Глубина</th>"
            output += u"<th>Отказы</th>"
            output += u"</tr></thead>\n"

            output += u"<tbody>\n"
            for row in data["data"]:
                year = row["date"][:4]
                month = int(row["date"][4:6])
                output += u"<tr>\n"
                output += u"<td>%s, %s</td>\n" % (months[month-1], year)
                output += u"<td>%s</td>\n" % fmt(row["visitors"])
                output += u"<td>%s</td>\n" % fmt(row["visits"])
                output += u"<td>%s</td>\n" % fmt(row["page_views"])
                output += u"<td>%.1f</td>\n" % row["depth"]
                output += u"<td>%u%%</td>\n" % (100 * row["denial"])
                output += u"</tr>\n"

            output += u"</tbody>\n</table>\n"
            return output
    except Exception, e:
        import traceback
        print "error  : could not display metrika table: %s" % e
        print traceback.format_exc(e)
        return u"При попытке построения таблицы возникла ошибка."


def similar_posts():
    try:
        labels = set(get_page_labels(page)) & set(["blog", "podcast", "guests"])
        if not labels:
            return ""

        main_label = labels.pop()

        similar = []

        meidx = None
        for p in sorted(pages, key=lambda p: p.get("date")):
            if not p.get("date"):
                continue
            if p.url == page.url:
                meidx = len(similar)
            elif "draft" in page["labels"]:
                continue
            if main_label in get_page_labels(p):
                similar.append(p)

        if meidx is None:
            return ""

        start = max(meidx - 2, 0)
        start = min(start, len(similar) - 5)
        similar = similar[start:start+5]

        if not similar:
            return ""

        months = [u"январь", u"февраль", u"март", u"апрель", u"май", u"июнь",
            u"июль", u"август", u"сентябрь", u"октябрь", u"ноябрь", u"декабрь"]

        items = []
        for p in similar:
            pd = get_page_date(p)
            month = int(time.strftime("%m", pd))
            year = time.strftime("%Y", pd)
            item = u"<div class=\"date\">%s %s</div>" % (months[month-1], year)

            if p.url == page.url:
                item += u"<a class=\"current\">%s</a>" % p["title"]
            else:
                item += u"<a href=\"%s\">%s</a>" % (fix_url(p.url), p["title"])

            items.append(item)

        output = u"<div id=\"similar\"><table><tbody><tr>\n"
        for item in items:
            output += u"<td>%s</td>\n" % item
        output += u"</tr></tbody></table></div>\n"

        return output
    except Exception, e:
        print "error  : coult not render similar posts: %s" % e
        return "<!-- error rendering similar posts -->\n"


def recent_blog_posts(limit=9):
    """Renders some recent blog posts as tiles."""
    tiles = []

    for page in sorted(macros("pages"), key=lambda p: p.get("date"), reverse=True):
        if "date" not in page:
            continue

        labels = get_page_labels(page)

        if "blog" not in labels:
            continue

        if "draft" in labels:
            continue

        if "poster" not in page:
            continue

        tiles.append({
            "link": page.url,
            "title": page["title"],
            "image": "input/" + page["poster"].encode("utf-8")
        })

    from plugins import Tiles
    return Tiles([(None, tiles[:limit])]).render()



def show_projects(filename):
    output = u"<table class='projects'>\n"
    output += u"<thead><tr><th>Проект</th><th/><th/></tr></thead>\n"
    output += u"<tbody>\n"

    raw_data = open("input/" + filename, "rb").read().decode("utf-8")
    lines = [l.split(";") for l in raw_data.strip().split("\n") if not l.startswith("#")]

    for parts in sorted(lines, key=lambda p: (-float(p[1]), p[0])):
        try:
            name, progress, link, comment = parts
            output += u"<tr>"

            if link:
                output += u"<td><a href='%s'>%s</a></td>" % (link, name)
            else:
                output += u"<td>%s</td>" % name

            if int(progress) == 1:
                output += u"<td>&#x2713;</td>"
            else:
                output += u"<td/>"

            output += u"<td>%s</td>" % comment

            output += u"</tr>\n"
        except ValueError, e:
            print "error  : bad project line: %s" % ";".join(parts).encode("utf-8")

    output += u"</tbody>\n"
    output += u"</table>\n"

    return output


def last_guests(columns=3):
    """Вывод картинок последних гостей."""
    from plugins import Tiles

    tiles = []

    for page in sorted(pages, key=lambda p: p.get("date"), reverse=True):
        labels = get_page_labels(page)

        if "photo" not in labels:
            continue

        if "guests" not in labels:
            continue

        if "draft" in labels:
            continue

        tiles.append({
            "link": page.url,
            "title": page["title"],
            "image": "input/" + page["image"],
        })

    return Tiles([(None, tiles[:6])]).render()


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


def album(tiles, columns=3):
    if columns == 4:
        sizes = (240, 160)
    else:
        sizes = (326, 233)

    for tile in tiles:
        tile["image"] = "input/" + tile["link"]
    return Tiles([(None, tiles)], sizes).render(
        css_class="album", columns=columns)


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
    elif "residents" in labels:
        _t = title[0].lower() + title[1:]
        title = u"<a href='/residents/'>Поселенцы</a>: %s" % _t

    return title


def wide_image():
    img = page.get("wideimage")
    if not img:
        return ""

    html = u"<div class='wide'>\n<img src='%s' alt='wide'/>" % img
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

    for p in videos:
        print p.fname, p["date"]

    for v in videos:
        print v.fname

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


def meta(key):
    if key not in page:
        print "warning: page %s has no meta header '%s'" % (page.fname, key)
    else:
        return page[key]


def hook_html_typo(html):
    html = html.replace(u".\n", u".&nbsp; ")
    return html


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
