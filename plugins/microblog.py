# encoding=utf-8

"""Microblog plugin for Poole

This plugin reads status updates from a plain text file and creates an RSS
feed.  This plugin is enabled with the following code:

    from plugins.microblog import *
    MICROBLOG_SOURCE = "input/status/messages.txt"
    MICROBLOG_FEED = "output/microblog.xml"
    MICROBLOG_URL = "http://umonkey.net/status/"

    # Optional settings.
    MICROBLOG_LANG = "rus"
    MICROBLOG_TITLE = u"Микроблог"
    MICROBLOG_DESCRIPTION = u"Ссылки и короткие заметки."
"""

import email.utils
import microblog
import hashlib
import os
import re
import sys
import tempfile
import time
import urllib
import urlparse
from xml.sax.saxutils import escape

from plugins import macros, fix_url_unicode


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"
__version__ = "1.0"


WEEKDAYS = (u"понедельник", u"вторник", u"среда", u"четверг", u"пятница", u"суббота", u"воскресенье")

REPLACE = [
    (u". ", u".&nbsp; "),
    (u" -- ", u"&nbsp;— "),
    (u" — ", u"&nbsp;— "),
]


def autoreplace(text):
    for s, d in REPLACE:
        text = text.replace(s, d)
    return text


def autolink(text):
    words = []

    link_count = 0
    link_index = link_href = None

    for word in text.split(" "):
        if word.startswith("#") and macros("MICROBLOG_STRIP_HASHTAGS"):
            continue
        if word.startswith("http://"):
            parts = urlparse.urlparse(word)
            link_href = fix_url_unicode(word)
            link_index = len(words)
            word = "<a href='%s'>%s</a>" % (link_href, parts.netloc)
            link_count += 1
        words.append(word)

    if link_count == 1:
        del words[link_index]
        message = u" ".join(words)
        message = re.sub("^([^,.:!?]+)", "<a href=\"%s\">\\1</a>" % link_href, message, count=1)
        return message

    return " ".join(words).strip(":")


def get_config():
    config = {}

    config["source"] = macros("MICROBLOG_SOURCE")
    if config["source"] is None:
        return

    if not os.path.exists(config["source"]):
        print "warning: file %s does not exist (microblog source)" % source
        return

    config["feed"] = macros("MICROBLOG_FEED")
    if config["feed"]:
        config["feed_url"] = macros("BASE_URL") + "/" + config["feed"][7:]

    config["url"] = macros("MICROBLOG_URL")
    config["lang"] = macros("MICROBLOG_LANG", "eng")
    config["title"] = macros("MICROBLOG_TITLE", "Microblog")
    config["description"] = macros("MICROBLOG_DESCRIPTION", "Status updates.")

    return config


def hook_preconvert_microblog():
    config = get_config()
    if config is None:
        return

    if not config.get("MICROBLOG_FEED"):
        print "info   : MICROBLOG_FEED not set -- not rendering."
        return

    started_on = time.time()

    xml = "<?xml version='1.0' encoding='utf-8'?>\n"
    xml += "<rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom'>\n"
    xml += "<channel>\n"
    xml += "<atom:link href='%s' rel='self' type='application/rss+xml'/>\n" % config["feed_url"]
    xml += "<language>%s</language>\n" % config["lang"]
    xml += "<link>%s</link>\n" % config["url"]
    xml += u"<description>%s</description>\n" % config["description"]
    xml += u"<title>%s</title>\n" % config["title"]

    messages = open(config["source"], "rb").read().strip().decode("utf-8").split("\n")
    messages.sort(reverse=True)

    for message in messages[:20]:
        _date, _time, status = message.split(" ", 2)

        # Fix UTF characters.
        words = []
        for word in status.split(" "):
            if word.startswith("#") and macros("MICROBLOG_STRIP_HASHTAGS"):
                continue
            if "://" in word and "%" not in word:
                word = fix_url_unicode(word)
            words.append(word)
        status = " ".join(words)

        link = guid = "%s#%s-%s" % (config["url"], _date, _time)
        for word in words:
            if "://" in word:
                link = word
                break

        ts = time.strptime(_date + " " + _time, "%Y-%m-%d %H:%M:%S")
        pubDate = email.utils.formatdate(time.mktime(ts))

        xml += "<item>\n"
        xml += "\t<title>%s</title>\n" % escape(status)
        xml += "\t<link>%s</link>\n" % link
        xml += "\t<guid>%s</guid>\n" % guid
        xml += "\t<pubDate>%s</pubDate>\n" % pubDate
        xml += "</item>\n"

    xml += "</channel>\n"
    xml += "</rss>\n"

    with open(config["feed"], "wb") as out:
        out.write(xml.encode("utf-8"))
        print "info   : wrote %s, took %u seconds." % (config["feed"], time.time() - started_on)


def microblog():
    """Template function that renders the microblog."""
    config = get_config()
    if config is None:
        return "<!-- microblog is not properly configured -->"

    embed_media = macros("microblog_embed_media")
    if not embed_media:
        print "debug  : function microblog_embed_media not defined, not embedding media."

    output = u""

    raw = open(config["source"], "rb").read().decode("utf-8")
    messages = raw.strip().split("\n")

    output += u"<ul class='microblog'>\n"

    for idx, message in enumerate(reversed(messages[-100:])):
        ts = time.strptime(message[:19], "%Y-%m-%d %H:%M:%S")
        message = message[20:]

        link_id = time.strftime("%Y%m%d%H%M", ts)
        weekday = WEEKDAYS[ts.tm_wday]

        message = autoreplace(message)
        message = autolink(message)

        output += "<li id='%s'>%s" % (link_id, message)

        if embed_media is not None and idx < 20:
            output += embed_media(message)

        output += u"<p class='timestamp'><a href='#%s'>%s (%s)</a></p>" % (link_id, time.strftime("%d.%m.%y, %H:%M", ts), weekday)

        output += u"</li>\n"

    output += u"</ul>\n"
    return output


def microblog_by_date(days=30):
    """Renders microblog entries grouped by date."""
    config = get_config()
    if config is None:
        return "<!-- microblog is not properly configured -->"

    embed_media = macros("microblog_embed_media")
    if not embed_media:
        print "debug  : function microblog_embed_media not defined, not embedding media."

    output = u""

    raw = open(config["source"], "rb").read().decode("utf-8")

    messages = {}
    for message in raw.strip().splitlines():
        ts = time.strptime(message[:19], "%Y-%m-%d %H:%M:%S")
        dt = time.strftime("%Y%m%d", ts)
        if dt not in messages:
            messages[dt] = []
        messages[dt].append((ts, message[20:]))

    output += u"<ul class='microblog'>\n"

    for date_idx, (date, items) in enumerate(sorted(messages.items(), reverse=True)[:days]):
        items.sort()

        output += u"<li class=\"date\">\n"
        output += u"<span>%s</span>\n" % time.strftime("%d.%m", items[0][0])
        output += u"<ul class=\"messages\">\n"

        for message_idx, (ts, message) in enumerate(items):
            message = autolink(autoreplace(message))

            output += u"<li>"
            output += message
            if embed_media is not None and date_idx < 5:
                output += embed_media(message)
            # output += u"<p class='timestamp'><a href='#%s'>%s (%s)</a></p>" % (link_id, time.strftime("%d.%m.%y, %H:%M", ts), weekday)
            output += u"</li>\n"

        output += u"</ul>\n"

    output += "</ul>"
    return output

    for idx, message in enumerate(reversed(messages[-100:])):
        ts = time.strptime(message[:19], "%Y-%m-%d %H:%M:%S")
        message = message[20:]

        link_id = time.strftime("%Y%m%d%H%M", ts)
        weekday = WEEKDAYS[ts.tm_wday]

        output += "<li id='%s'>" % link_id
        output += autolink(message).replace(". ", ".&nbsp; ")

        if embed_media is not None and idx < 20:
            output += embed_media(message)

        output += u"<p class='timestamp'><a href='#%s'>%s (%s)</a></p>" % (link_id, time.strftime("%d.%m.%y, %H:%M", ts), weekday)

        output += u"</li>\n"

    output += u"</ul>\n"
    return output


def microblog_light(count=5):
    """Renders latest count entries from the microblog as a simple list."""
    config = get_config()
    if config is None:
        return "<!-- error rendering microblog -->"

    raw = open(config["source"], "rb").read().decode("utf-8")
    messages = raw.strip().split("\n")

    output = u"<ul class='microblog_light'>\n"
    for message in reversed(messages[-5:]):
        ts = time.strptime(message[:19], "%Y-%m-%d %H:%M:%S")
        message = message[20:]
        output += "<li>" + autolink(message).replace(". ", ".&nbsp; ") + u"</li>\n"

    output += u"</ul>\n"
    return output


__all__ = [
    "hook_preconvert_microblog",
    "microblog",
    "microblog_by_date",
    "microblog_light",
]
