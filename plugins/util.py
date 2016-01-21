# encoding=utf-8

import sys


__all__ = ["macros", "utf", "deutf", "log_warning", "log_debug"]


def macros(k, v=None):
    """Access properties of the macros module, e.g. pages, or page."""
    return getattr(sys.modules["macros"], k, v)


def utf(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return s


def deutf(s):
    if isinstance(s, str):
        return s.decode("utf-8")
    return unicode(s)


def log_warning(msg, *args, **kwargs):
    msg = msg.format(*args, **kwargs)
    print "warning: %s" % msg.strip()


def log_debug(msg, *args, **kwargs):
    msg = msg.format(*args, **kwargs)
    print "debug  : %s" % msg.strip()
