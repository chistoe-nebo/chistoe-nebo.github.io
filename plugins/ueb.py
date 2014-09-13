# encoding=utf-8

"""Universal Edit Button plugin for Poole

This plugin adds the Universal Edit Button code to all pages.  To enable it,
load the script in macros.py and set the editor URL pattern, like this:

    from plugins.ueb import *
    UEB_PATTERN = "http://example.com/editor?page=%s"
"""

import sys

from plugins import macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"


def _add_to_head(html, header):
    """Adds a new header before the closing HEAD tag."""
    return html.replace("</head>", header.strip() + "\n</head>")


def hook_html_ueb(html):
    """Injects a link to the page editor to all pages.  UEB_PATTERN must be set
    in macros.py for this to work.  The %s in the pattern is replaced with the
    page file name."""
    pattern = macros("UEB_PATTERN")
    if pattern is not None:
        link = pattern % macros("page").fname[2:]
        html = _add_to_head(html, "<link rel='alternate' type='application/wiki' title='Edit this page' href='%s'/>" % link)
    return html


__all__ = [
    "hook_html_ueb",
]
