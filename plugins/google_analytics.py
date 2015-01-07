# encoding=utf-8

from plugins import macros


TEMPLATE = """<!-- Google Analytics --><script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){ (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o), m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m) })(window,document,'script','//www.google-analytics.com/analytics.js','ga'); ga('create', '{id}', 'auto'); ga('send', 'pageview');</script>\n"""

def hook_html_google_analytics(html):
    counter_id = macros("GOOGLE_ANALYTICS_ID")
    if counter_id is not None:
        code = TEMPLATE.replace("{id}", counter_id)
        html = html.replace("</body>", code + "</body>")
    return html


__all__ = [
    "hook_html_google_analytics",
]
