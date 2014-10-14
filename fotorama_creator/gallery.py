__author__ = 'jevgenik'

import os, shutil
import pkg_resources
from string import Template
from os.path import join as path_join, dirname, isfile
from PIL import Image
import cgi
import fnmatch
import re
import time
from multiprocessing import Pool, cpu_count
import ConfigParser


class Gallery:
  def __init__(self, output_dir, photo_dir, **kwargs):
    self.path = output_dir
    self._source_photo_path = photo_dir
    self.index_path = path_join(self.path, 'index.html')
    self.photo_path = path_join(self.path, 'photos')
    self.thumbs_path = path_join(self.path, 'thumbs')

    self.title = kwargs.get('title') or "My fotorama gallery"
    self.sorting = kwargs.get('sort')
    self.thumb_size = (180, 180)

    self.picasa_star = kwargs.get('picasa_star')

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

    print "Creating thumbnails. Using %d processes" % cpu_count()

    pool = Pool(processes=cpu_count())
    pool.map(_create_thumbnail_parallel, map(lambda f: (path_join(self.photo_path, f), path_join(self.thumbs_path, f), self.thumb_size), self.images))
    pool.close()

    print "Thumbnails for %d images created" % len(self.images)


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

    if self.picasa_star:
      print "Creating gallery only from Picasa starred photos"

    pattern = re.compile(fnmatch.translate('*.jpg'), re.IGNORECASE)

    self.images = []
    for root, dirs, files in os.walk(self.photo_path, topdown=True):
      images = [os.path.relpath(path_join(root, j), self.photo_path) for j in files if pattern.match(j)]

      if self.picasa_star:
        images = _filter_picasa_starred(root, images)

      if self.sorting == 'date':
        images.sort(key=lambda i: _get_image_date(path_join(self.photo_path, i)))
      else:
        images.sort()

      self.images += images


def _filter_picasa_starred(folder, images):
  ini = path_join(folder, '.picasa.ini')
  if not isfile(ini):
    return []

  cfg = ConfigParser.ConfigParser()
  cfg.read(ini)

  cfg.defaults().setdefault("star", "false")
  starred = [img for img in cfg.sections() if cfg.getboolean(img, "star")]

  return [i for i in images if os.path.basename(i) in starred]

def _get_image_date(file):
  with Image.open(file) as image:
    info = image._getexif()
    if info and 0x0132 in info:
      return time.strptime(info.get(0x0132), '%Y:%m:%d %H:%M:%S')
    else:
      return time.gmtime(os.path.getctime(file))

def _create_thumbnail_parallel(input):
  (image_file, thumb_file, thumb_size) = input

  print "Creating thumbnail for:", image_file
  with Image.open(image_file) as image:
    image.thumbnail(thumb_size, Image.ANTIALIAS)

    dir = dirname(thumb_file)
    if not os.path.exists(dir):
      print "Creating dir:", dir
      os.makedirs(dir)
    image.save(thumb_file, image.format)