# encoding=utf-8


import urlparse

from plugins import Thumbnail, element, macros


__all__ = ["image"]


def image(url, title=None, description=None, width=None, cls=None):
    """Вставка изображения в страницу, с параметрами."""
    page = macros("page")

    if description and cls is None:
        cls = "right"

    if width is None:
        width = macros("DEFAULT_IMAGE_WIDTH", 1000)

    image_url = urlparse.urljoin(page.url, url)
    image_path = "input/" + image_url.lstrip("/")

    thumbnail = Thumbnail(image_path, width=width, height=width, fit=False)

    html = element("img", {
        "src": thumbnail.get_url(),
        "alt": title,
        "itemprop": "contentUrl",
        "style": "width: %upx; height: %upx" % (thumbnail.width, thumbnail.height),
    })

    html = element("a", {
        "class": "picture",
        "href": image_url,
        "title": title,
    }, html)

    deutf = lambda s: unicode(s, "utf-8") if isinstance(s, str) else unicode(s)

    if description:
        html += element("div", {
            "class": "imgdesc figuredesc",
            "itemprop": "description",
        }, u"<p>%s</p>" % deutf(description))

    if title:
        html += element("figcaption", {
            "class": "imgdesc",
            "itemprop": "caption",
        }, u"<p>%s</p>" % deutf(title))

    fig_cls = "figure figure_%u" % thumbnail.width
    if title:
        fig_cls += " with_title"
    if description:
        fig_cls += " with_desc"
    if cls is not None:
        fig_cls += " " + cls

    html = element("figure", {
        "class": fig_cls,
        "itemscope": "itemscope",
        "itemtype": "http://schema.org/ImageObject",
    }, html)

    return html
