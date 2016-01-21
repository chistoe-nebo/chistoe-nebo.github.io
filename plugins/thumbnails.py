# encoding=utf-8

import hashlib
import Image
import ImageFilter
import os

from util import macros


__all__ = ["Thumbnail"]


def copy_file(src, dst):
    if os.path.exists(dst):
        os.unlink(dst)

    folder = os.path.dirname(dst)
    if not os.path.exists(folder):
        os.makedirs(folder)

    os.link(src, dst)


class Thumbnail(object):
    def __init__(self, src_path, width, height=None):
        """Creates a thumbnail from the specified file."""
        if not os.path.exists(src_path):
            raise ValueError("image %s not found" % src_path)

        fit = height is None  # else crop

        self.src_path = src_path
        self.dst_path = None
        self.dst_link = None
        self.width = None
        self.height = None

        output = macros("output")
        parts = os.path.splitext(os.path.basename(src_path))
        folder = os.path.dirname(os.path.relpath(src_path, "input"))

        if fit:
            img = Image.open(src_path)
            if img.size[0] <= width:
                # source image is smaller than required, no transformation
                name = os.path.basename(src_path)
                self.dst_link = folder + "/" + name
                self.dst_path = os.path.join(output, self.dst_link)
                self.width = img.size[0]
                self.height = img.size[1]
                return

        if fit:
            dst_name = "%s_%u%s" % (parts[0], width, parts[1])
        else:
            dst_name = "%s_%ux%u%s" % (parts[0], width, height, parts[1])

        self.dst_path = os.path.join(macros("output"), folder, dst_name)
        self.dst_link = "%s/%s" % (folder, dst_name)

        self.prepare(width, height, fit)

    def __repr__(self):
        return "<Thumbnail %s (%ux%u)>" % (self.src_path, self.width, self.height)

    def prepare(self, width, height, fit):
        """Creates the requested thumbnail."""
        if os.path.exists(self.dst_path):
            self.update_size()
            return

        crop = not fit

        cache_key = hashlib.sha1(open(self.src_path, "rb").read()).hexdigest()
        if fit:
            cache_path = "cache/thumbnail/%s_%u" % (cache_key, width)
        else:
            cache_path = "cache/thumbnail/%s_%ux%u" % (cache_key, width, height)

        if os.path.exists(cache_path):
            copy_file(cache_path, self.dst_path)
            self.update_size()
            print "info   : thumbnail %s (%ux%u) created (from cache)" % (self.dst_link, self.width, self.height)

        else:
            try:
                img = Image.open(self.src_path)
            except Exception, e:
                print "error  : could not open %s: %s" % (self.src_path, e)
                raise

            ratio = float(img.size[0]) / float(img.size[1])

            new_width = width
            new_height = int(new_width / ratio)

            if crop and new_height < height:
                new_height = height
                new_width = new_height * ratio
            elif fit and new_height > height:
                new_height = height
                new_width = new_height * ratio

            img = img.resize((int(new_width), int(new_height)), Image.ANTIALIAS)

            if crop:
                if new_width > width:
                    shift = int((new_width - width) / 2)
                    crop_rect = (shift, 0, shift + width, height)
                else:
                    shift = (new_height - height) / 2
                    crop_rect = (0, shift, width, shift + height)

                img = img.crop(crop_rect)

            img.filter(ImageFilter.SHARPEN)

            img.save(self.dst_path, quality=90)
            copy_file(self.dst_path, cache_path)
            self.update_size()

            print "info   : thumbnail %s (%ux%u) created" % (self.dst_link, self.width, self.height)

    def update_size(self):
        img = Image.open(self.dst_path)
        self.width = img.size[0]
        self.height = img.size[1]

    def get_url(self):
        return "/" + self.dst_link
