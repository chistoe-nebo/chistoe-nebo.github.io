# vim: set fileencoding=utf-8 tw=0:

"""Yandex.Metrika plugin for Poole

This plugin adds Yandex.Metrika tracking code to all pages.  To enable it, load
the script and specify your identifier, like this:

    from plugins.yandex_metrika import *
    YANDEX_METRIKA_ID = "123456"
"""

import sys

from plugins import macros


__author__ = "Justin Forest"
__email__ = "hex@umonkey.net"
__license__ = "GPL"

TEMPLATE = '<!-- Yandex.Metrika counter --><script type="text/javascript">(function (d, w, c) { (w[c] = w[c] || []).push(function() { try { w.yaCounter%(id)s = new Ya.Metrika({id:%(id)s, accurateTrackBounce:true}); } catch(e) {} }); var n = d.getElementsByTagName("script")[0], s = d.createElement("script"), f = function () { n.parentNode.insertBefore(s, n); }; s.type = "text/javascript"; s.async = true; s.src = (d.location.protocol == "https:" ? "https:" : "http:") + "//mc.yandex.ru/metrika/watch.js"; if (w.opera == "[object Opera]") { d.addEventListener("DOMContentLoaded", f); } else { f(); } })(document, window, "yandex_metrika_callbacks");</script><noscript><div><img src="//mc.yandex.ru/watch/%(id)s" style="position:absolute; left:-9999px;" alt="" /></div></noscript><!-- /Yandex.Metrika counter -->\n'


def hook_html_yandex_metrika(html):
    """Injects the HTML code of the counter.  Works onl if YANDEX_METRIKA_ID is
    set in macros.py."""
    site_id = macros("YANDEX_METRIKA_ID")
    if site_id is not None:
        counter = TEMPLATE % {"id": str(site_id)}
        html = html.replace("</body>", counter + "</body>")
    return html


def hook_preconvert_yandex_metrika():
    """Produces a warning if YANDEX_METRIKA_ID is not set in macros.py"""
    if macros("YANDEX_METRIKA_ID") is None:
        print >> sys.stderr, "warning: YANDEX_METRIKA_ID not set in macros.py"


__all__ = [
    "hook_html_yandex_metrika",
    "hook_preconvert_yandex_metrika",
]
