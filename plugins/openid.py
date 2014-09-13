# encoding=utf-8

"""OpenID delegation plugin for Poole"""

import sys

from plugins import macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"
__version__ = "1.0"


def hook_html_myopenid(html):
    name = macros("MYOPENID_NAME")
    if name is not None and macros("page").url == "index.html":
        add = u"<!-- OpenID -->\n"
        add += u"<link rel=\"openid.server\" href=\"http://www.myopenid.com/server\"/>\n"
        add += u"<link rel=\"openid.delegate\" href=\"http://%s.myopenid.com/\"/>\n" % name
        add += u"<link rel=\"openid2.local_id\" href=\"http://%s.myopenid.com\"/>\n" % name
        add += u"<link rel=\"openid2.provider\" href=\"http://www.myopenid.com/server\"/>\n"

        html = html.replace("</head>", add + "</head>")

    return html


__all__ = [
    "hook_html_myopenid",
]
