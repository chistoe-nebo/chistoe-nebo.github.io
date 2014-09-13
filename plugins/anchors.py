# encoding=utf-8

"""Poole plugin to add anchor and paragraph anchors

The process is split in two hooks: first, post-convert, adds special
markers to paragraphs that need a self-pointing anchor.  Anchors
themselves are rendered in the html hook, which is called after the RSS
feeds were generated.  This saves the RSS feed from garbage.

Configuration.  Defaults can be set using variables
ADD_PARAGRAPH_ANCHORS and ADD_HEADER_ANCHORS, which are True by default.
On a per-page basis anchors can be disabled by setting to "no"
properties "para-anchors", "head-anchors" and "anchors" (implies both).
"""


import binascii
import re
import sys

from plugins import macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"
__version__ = "1.0"


ADD_PARAGRAPH_ANCHORS = True
ADD_HEADER_ANCHORS = True
ANCHOR_SYMBOL = "#"


def hook_postconvert_anchors():
    add_para_anchors = macros("ADD_PARAGRAPH_ANCHORS", True)
    add_head_anchors = macros("ADD_HEADER_ANCHORS", True)

    def has_para_anchors(page):
        if not add_para_anchors:
            return False
        if page.get("anchors") == "no":
            return False
        if page.get("para_anchors") == "no":
            return False
        return True

    def has_head_anchors(page):
        if not add_head_anchors:
            return False
        if page.get("anchors") == "no":
            return False
        if page.get("header_anchors") == "no":
            return False
        return True

    for page in macros("pages", []):
        html = page.html
        if has_head_anchors(page):
            html = _add_head_anchors(html)
        if has_para_anchors(page):
            html = _add_para_anchors(html)
        page.html = html


def _crc32(value):
    return "%08x" % (binascii.crc32(value.strip().encode("utf-8")) & 0xffffffff)


def _add_head_anchors(text):
    headers = []
    for match in re.findall("(^<(h\d)>((?:(?!</h\d>).)*)</h\d>$)", text, re.S | re.M):
        _hash = _crc32(match[2])
        _repl = u"<%s id='%s' class='with-anchor'>%s</%s>" % (match[1], _hash, match[2], match[1])
        text = text.replace(match[0], _repl)
        headers.append((match[1], _hash, match[2]))

    return text


def _add_para_anchors(text):
    idx = 1

    for match in re.findall("(^<p>((?:(?!/p).)*)</p>$)", text, re.S | re.M):
        if "<img" in match[1]:
            continue

        _hash = "%02u" % idx
        idx += 1

        repl = u"<p id='%s' class='with-anchor'>%s</p>" % (_hash, match[1])
        text = text.replace(match[0], repl)
    return text


def hook_html_anchors(html):
    """Adds self-pointing anchors to paragraphs marked with the with-anchor
    class."""
    symbol = macros("ANCHOR_SYMBOL", "#")
    title = macros("PARA_ANCHOR_TITLE", "Link to this paragraph")

    idx = 1
    pattern = "<p id='([^']+)' class='with-anchor'>"
    for match in re.finditer(pattern, html):
        symbol = "%02u" % idx
        idx += 1

        new_html = match.group(0)
        new_html += u"<a href='#%s' class='anchor' title='%s'>%s</a>" \
            % (match.group(1), title, symbol)
        html = html.replace(match.group(0), new_html)

    return html


__all__ = [
    "hook_postconvert_anchors",
    "hook_html_anchors",
    "ADD_PARAGRAPH_ANCHORS",
    "ADD_HEADER_ANCHORS",
]
