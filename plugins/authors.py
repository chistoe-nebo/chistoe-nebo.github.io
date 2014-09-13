# encoding=utf-8

import sys

from plugins import macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"


def get_page_author(page):
    """Describes the page author with a dictionary.  Authors list is read
    from the AUTHORS macro, page authors are defined with the 'author'
    property."""
    if "_author_info_cache" in page:
        return page["_author_info_cache"]

    authors = macros("AUTHORS")
    if authors is None:
        page["_author_info_cache"] = None
        return None

    found = None

    if "author" in page:
        found = [a for a in authors if a["name"] == page["author"]]

    if not found:
        found = [a for a in authors if a.get("default")]

    if found:
        page["_author_info_cache"] = found[0]
        return found[0]


def hook_html_link_rel_author(html):
    page = macros("page")

    author = get_page_author(page)
    if author is not None and "link" in author:
        extra = "<link rel='author' href='%s'/>\n" % author["link"]
        html = html.replace("</head>", extra + "</head>")

    return html


__all__ = [
    "get_page_author",
    "hook_html_link_rel_author",
]
