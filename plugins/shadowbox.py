# encoding=utf-8

import sys

from plugins import macros


SHADOWBOX_PATH = "/files/shadowbox"

SHADOWBOX_CODE = """<link rel='stylesheet' type='text/css' href='%(path)s/shadowbox.css'/>
<script type="text/javascript" src="%(path)s/jquery.pack.js"></script>
<script type="text/javascript" src="%(path)s/shadowbox.js"></script>
<script type="text/javascript">Shadowbox.init({players:['img']});</script>
"""

def hook_html_shadowbox(html):
    if " rel=\"shadowbox" in html or " rel='shadowbox" in html:
        code = SHADOWBOX_CODE % {"path": SHADOWBOX_PATH}
        html = html.replace("</head>", code + "</head>")

    return html


__all__ = [
    "hook_html_shadowbox",
    "SHADOWBOX_PATH",
]
