# encoding=utf-8

import re


__all__ = ["hook_html_typo", "typo"]


def typo(text):
    utf = isinstance(text, str)
    if utf:
        text = text.decode("utf-8")

    text = text.replace(u".  ", u".&nbsp; ")
    text = text.replace(u" - ", u"&nbsp;— ")
    text = text.replace(u" -- ", u"&nbsp;— ")

    # Non-breaking dash for number ranges.
    # http://www.fileformat.info/info/unicode/char/2011/index.htm
    # FIXME: ломает ссылки итп.
    #text = re.sub(u"(\\d)-(\\d)", u"\\1\u2011\\2", text)



    # Склеивание предлогов и союзов.
    text = re.sub(u"\s+(в|на|и|у|из|под|перед|с|для|к)\s+", u" \\1&nbsp;", text)
    text = re.sub(u"\s+(В|На|И|У|Из|Под|Перед|С|Для|К)\s+", u" \\1&nbsp;", text)

    # Добавление пробелов между предложениями.
    text = re.sub(u"\.\s+([А-Я])", u".&nbsp; \\1", text)

    if utf:
        text = text.encode("utf-8")

    return text


def hook_html_typo(html):
    return typo(html)
