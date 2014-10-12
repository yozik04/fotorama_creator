__author__ = 'jevgenik'

import os, shutil
import pkg_resources
from string import Template
from os.path import join as path_join, dirname
from PIL import Image
import cgi
import fnmatch
import re
import time


class Gallery:
  def __init__(self, output_dir, photo_dir, title, sort):
    self.path = output_dir
    self.title = title
    self.index_path = path_join(self.path, 'index.html')
    self.photo_path = path_join(self.path, 'photos')
    self.thumbs_path = path_join(self.path, 'thumbs')
    self.sorting = sort
    self.thumb_size = (180, 180)
    self._source_photo_path = photo_dir


  def create(self):
    if os.path.isfile(self.index_path):
      raise Exception('index.html file already exists in current dir. Can not proceed!')

    if not os.path.islink(self.photo_path):
      os.symlink(self._source_photo_path, self.photo_path)
      print 'Symlink for photo dir "%s" created' % self._source_photo_path

    self.copy_assets()
    self.create_thumbnails()
    self.create_index()

    print "Gallery ready!"


  def create_thumbnails(self):
    self._scan_photo_path()

    if not os.path.isdir(self.thumbs_path):
      os.mkdir(self.thumbs_path)
      print "Thumbnails folder created"

    for image_file in self.images:
      print "Creating thumbnail for:", image_file
      with Image.open(path_join(self.photo_path, image_file)) as image:
        image.thumbnail(self.thumb_size, Image.ANTIALIAS)

        thumb_file = path_join(self.thumbs_path, image_file)
        dir = dirname(thumb_file)
        if not os.path.exists(dir):
          print "Creating dir:", dir
          os.makedirs(dir)
        image.save(thumb_file, image.format)

    print "Thumbnails created"


  def copy_assets(self):
    source = pkg_resources.resource_filename(__name__, path_join("data", "static"))
    try:
      shutil.copytree(source, path_join(self.path, "static"))
      print "Assets copied"
    except OSError as e:
      print 'Static folder was not copied because of an error:', str(e)


  def create_index(self):
    self._scan_photo_path()

    html = ''
    for image_file in self.images:
      with Image.open(path_join(self.thumbs_path, image_file)) as image:
        (width, height) = image.size
        html += '<a href="%s"><img src="%s" width="%d" height="%d"></a>' % (cgi.escape('photos/' + image_file), cgi.escape('thumbs/' + image_file), width, height)

    tpl = Template(open(pkg_resources.resource_filename(__name__, path_join("data", "template.html"))).read())
    content = tpl.substitute({"title": cgi.escape(self.title), "images": html})
    open(self.index_path, 'w').write(content)

    print "Index created"


  def _scan_photo_path(self):
    if hasattr(self, 'images'):
      return

    pattern = re.compile(fnmatch.translate('*.jpg'), re.IGNORECASE)

    self.images = []
    for root, dirs, files in os.walk(self.photo_path, topdown=True):
      images = [os.path.relpath(path_join(root, j), self.photo_path) for j in files if pattern.match(j)]

      if self.sorting == 'date':
        images.sort(key=self._get_image_date)
      else:
        images.sort()

      self.images += images

  def _get_image_date(self, file):
    with Image.open(path_join(self.photo_path, file)) as image:
      info = image._getexif()
      if info:
        return time.strptime(info.get(0x0132), '%Y:%m:%d %H:%M:%S')
      else:
        return time.gmtime(os.path.getctime(file))