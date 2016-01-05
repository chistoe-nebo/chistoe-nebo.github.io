# encoding=utf-8

"""
Вывод информации о жителях поселения.
"""


import os

from plugins import macros, join_path, Tiles


__all__ = ["hook_postconvert_other_residents", "find_residents", "wide_image"]


def hook_postconvert_other_residents():
    residents = find_residents()

    for page in macros("pages"):
        if "residents" not in page.get_labels():
            continue

        tiles = [{
            "image": join_path(res.fname, res.get("thumbnail", "_thumbnail.jpg")),
            "link": res.url,
            "title": res["title"],
        } for res in residents
          if res.fname != page.fname]

        if not tiles:
            continue

        tiles_html = Tiles([(None, tiles)], (75, 75)).render(
                           css_class="other_residents",
                           columns=100)

        bonus = u"<div class='other'>"
        bonus += u"<h3>Познакомьтесь и с другими <a href='/residents/' title='Жители экопоселения Чистое небо'>нашими жителями</a>:</h3>"
        bonus += tiles_html
        bonus += u"</div>"

        page.html += bonus


def find_residents():
    label = "residents"
    pages = macros("pages")
    residents = [p for p in pages
                 if label in p.get_labels()
                 and p.get("hidden") != "yes"]
    residents.sort(key=lambda p: p["title"].lower())
    return residents


def wide_image():
    page = macros("page")

    if "residents" not in page.get_labels():
        return ""

    image_name = page.get("wideimage", "_wide.jpg")

    image_path = join_path(page.fname, image_name)
    if not os.path.exists(image_path):
        return ""

    image_url = join_path(page.url, image_name)

    if page.get("widetext"):
        html = u"<div class='wide'>"
        html += u"<div class='image' style='background-image:url(/%s)'></div>" % image_url
        if "wide_color" in page:
            html += u"<div class='text' style='background-color:#%s'>" % page["wide_color"]
        else:
            html += u"<div class='text'>"
        html += u"<h1>%s</h1>" % page["title"]
        html += u"<p>%s</p>" % page["widetext"]
        html += u"</div>"
    else:
        html = u"<div class='wide' style='background-image:url(/%s)'>" % image_url

    html += u"</div>\n"

    return html
