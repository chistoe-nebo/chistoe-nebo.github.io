# encoding=utf-8

"""Disqus plugin for Poole

This plugin adds Disqus comments to Poole websites with just a couple of lines
of code.  To enable it, load the script in macros.py and specify your Disqus
website id, like this:

    from plugins.disqus import *
    DISQUS_ID = "alice-blog"

To add the comment form and the discussion thread to a page, use the comments
function in your template, like this:

    <div id="comments">{{ comments() }}</div>

Comments can be disabled per page by using the "comments:no" property, like
this:

    title: Introduction
    comments: no

If there is a function named fix_url in macros.py, it's used to process all
URLs (e.g., to strip "index.html" to make local links prettier).
"""

import re
import sys

from plugins import macros, fix_url, get_page_labels


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"
__version__ = "1.0"


def page_has_comments(html):
    return '<div id="disqus_thread">' in html


def add_header(html, page, disqus_id):
    base_url = macros("BASE_URL", "")

    disqus_url = page.get("disqus_url", base_url + fix_url("/" + page.url))

    settings = ''
    settings += u"var disqus_url = '%s'; " % page.get("disqus_url", disqus_url)
    settings += u"var disqus_shortname = '%s'; " % disqus_id
    settings += u"var disqus_identifier = '%s'; " % page.url
    settings += u"var disqus_developer = (window.location.href.indexOf('http://127.0.0.1:') == 0); "
    settings += u"var disqus_title = '%s'; " % page["title"]

    header = "<script type='text/javascript'>%s</script>\n" % settings.strip()
    html = html.replace("</head>", header + "</head>")
    return html


def add_body(html, page, disqus_id):
    base_url = macros("BASE_URL", "")
    disqus_url = page.get("disqus_url", base_url + fix_url("/" + page.url))

    if page_has_comments(html):
        script_url = "http://%s.disqus.com/embed.js" % disqus_id
    elif '#disqus_thread' in page.html:
        script_url = "http://%s.disqus.com/count.js" % disqus_id
    else:
        return html

    script = '<script type="text/javascript"> (function() { var dsq = document.createElement(\'script\'); dsq.type = \'text/javascript\'; dsq.async = true; dsq.src = \'%s\'; (document.getElementsByTagName(\'head\')[0] || document.getElementsByTagName(\'body\')[0]).appendChild(dsq); })();</script>' % script_url
    return html.replace("</body>", script + "</body>")


def hook_html_disqus(html):
    """Inject required HTML code to pages that have comments enabled (i.e., not
    explicitly disabled by the comments:no property)."""
    disqus_id = macros("DISQUS_ID")
    if disqus_id:
        page = macros("page")
        if "draft" not in get_page_labels(page):
            html = add_header(html, page, disqus_id)
            html = add_body(html, page, disqus_id)
    return html


def comments():
    """Prints the comment form and displays existing comments, if the current
    page does not disable them.  Requires DISQUS_ID to be set in macros.py,
    otherwise produces a warning."""
    page = macros("page")
    if page.get("comments", "yes") == "yes" and "draft" not in get_page_labels(page):
        if macros("DISQUS_ID") is None:
            print >> sys.stderr, "warning: %s uses comments, " \
                "but DISQUS_ID not set in macros.py" % page.fname
            return ""
        return '<div id="disqus_thread"></div>'
    return ""


__all__ = [
    "comments",
    "hook_html_disqus",
]
