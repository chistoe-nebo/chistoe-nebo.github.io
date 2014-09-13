# encoding=utf-8

"""Poole plugin to embed podcasts
"""

import cgi
import os

from plugins import get_page_labels
from plugins import macros
from plugins import utf


PLAYER = u"""<audio controls="controls">
<source src="{file}" type="audio/mpeg"/>
<object type="application/x-shockwave-flash" data="{swf}" height="24" width="479">
<param name="movie" value="{swf}">
<param name="FlashVars" value="soundFile={file}&amp;titles={title}">
<param name="quality" value="high">
<param name="menu" value="false">
<param name="wmode" value="transparent">
</object>
</audio>
"""

def podcast(message):
    page = macros("page")

    audio = page.get("file", "")
    if not audio.endswith(".mp3"):
        print "warning: %s is NOT a podcast, no file." % page.fname
        return message

    html = PLAYER.format(
        swf="/files/audioplayer.swf",
        file=audio,
        title=page["title"]).rstrip()

    html += u"\n\n" + message.decode("utf-8")

    html += u"\n\n<p><a href='%s'>Скачать запись</a></p>" % audio

    return html


def hook_page_contents_audio(page):
    """Returns the audio page contents with an embedded player."""
    labels = get_page_labels(page)
    if "audio" not in labels:
        return None

    ogg = mp3 = None

    webdir = os.path.dirname(page.url)
    path = os.path.join("input", webdir)

    for fn in os.listdir(path):
        if fn.endswith(".ogg"):
            ogg = fn
        elif fn.endswith(".mp3"):
            mp3 = fn

    if page.get("file", "").endswith(".mp3"):
        mp3 = page["file"]
    if "file-ogg" in page:
        ogg = page["file-ogg"]

    if not ogg and not mp3:
        return None

    html = "<div class='audio'><audio controls='controls'>"
    if mp3:
        html += "<source src='%s' type='audio/mp3'/>" % mp3
    if ogg:
        html += "<source src='%s' type='audio/ogg'/>" % ogg
    html += "</audio></div>"

    html += u"<p class='dlaudio'>Скачать:"
    if mp3:
        html += " <a href='%s'>MP3</a>" % mp3
    if ogg:
        html += " <a href='%s'>Ogg Vorbis</a>" % ogg
    if int(page.get("download-count", "0")) > 0:
        html += u"; загружен %s раз" % page["download-count"]
    html += "</p>"

    html += page.html

    return html


__all__ = [
    "hook_page_contents_audio",
    "podcast"
]
