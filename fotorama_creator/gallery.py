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

INDEX_FILE = 'index.html'
ORIGINAL_DIR = 'photos'
OPTIMIZED_DIR = 'optimized'
THUMBNAIL_DIR = 'thumbs'

class Gallery:
  def __init__(self, output_dir, photo_dir, **kwargs):
    self.path = output_dir
    self._source_photo_path = photo_dir
    self.index_path = path_join(self.path, INDEX_FILE)
    self.photo_path = path_join(self.path, ORIGINAL_DIR)
    self.optimized_path = path_join(self.path, OPTIMIZED_DIR)
    self.thumbs_path = path_join(self.path, THUMBNAIL_DIR)

    self.title = kwargs.get('title') or "My fotorama gallery"
    self.sorting = kwargs.get('sort')
    self.sorting_global = kwargs.get('sort_global')
    self.force_thumbnails = kwargs.get('force_thumbnails')
    self.thumb_size = (180, 180)
    self.optimized_size = (1350, 1350)

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
    pool.map(_rotate_and_scale, map(lambda f: (path_join(self.photo_path, f), path_join(self.optimized_path, f), self.optimized_size, self.force_thumbnails), self.images))
    pool.map(_rotate_and_scale, map(lambda f: (path_join(self.optimized_path, f), path_join(self.thumbs_path, f), self.thumb_size, self.force_thumbnails), self.images))
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
        html += '<a href="%s"><img src="%s" data-full="%s" width="%d" height="%d"></a>' % (cgi.escape(OPTIMIZED_DIR + '/' + image_file), cgi.escape(THUMBNAIL_DIR + '/' + image_file), cgi.escape(ORIGINAL_DIR + '/' + image_file), width, height)

    tpl = Template(open(pkg_resources.resource_filename(__name__, path_join("data", "template.html"))).read())
    content = tpl.substitute({"title": cgi.escape(self.title), "images": html})
    open(self.index_path, 'w').write(content)

    print "Index created"


  def _scan_photo_path(self):
    if hasattr(self, 'images'):
      return

    if self.picasa_star:
      print "Creating gallery only from Picasa starred photos"

    if self.sorting_global:
      print "Using global sort by %s" % self.sorting
    else:
      print "Using folder sort by %s" % self.sorting

    pattern = re.compile('.*\.(jpg|jpeg)$', re.IGNORECASE)

    self.images = []
    for root, dirs, files in os.walk(self.photo_path, topdown=True):
      images = [os.path.relpath(path_join(root, j), self.photo_path) for j in files if pattern.match(j)]

      if self.picasa_star:
        images = _filter_picasa_starred(root, images)

      if not self.sorting_global:
        self._sort(images)

      self.images += images

    if self.sorting_global:
      self._sort(self.images)

  def _sort(self, images):
    if self.sorting == 'date':
      images.sort(key=lambda i: _get_image_date(path_join(self.photo_path, i)))
    else:
      images.sort()

def _filter_picasa_starred(folder, images):
  ini = path_join(folder, '.picasa.ini')
  if not isfile(ini):
    print '.picasa.ini not found in %s. Skipping...' % folder
    return []

  cfg = ConfigParser.ConfigParser()
  cfg.read(ini)

  cfg.defaults().setdefault("star", "false")
  starred = [img for img in cfg.sections() if cfg.getboolean(img, "star")]

  return [i for i in images if os.path.basename(i) in starred]

def _get_image_date(file):
  with Image.open(file) as image:
    info = image._getexif()
    if info and 36867 in info:
      return time.strptime(info.get(36867), '%Y:%m:%d %H:%M:%S')
    else:
      return time.gmtime(os.path.getctime(file))

def _rotate_and_scale(input):
  (in_file, out_file, thumb_size, force) = input
  if not force and os.path.isfile(out_file):
    print "Outfile already exists %s. Skipping..." % (out_file)
    return

  print "Auto rotating and scaling down to %s: %s -> %s" % (str(thumb_size), in_file, out_file)
  with Image.open(in_file) as image:
    image.thumbnail(thumb_size, Image.ANTIALIAS)
    image = _autorotate(image)

    dir = dirname(out_file)
    if not os.path.exists(dir):
      print "Creating directory:", dir
      os.makedirs(dir)
    image.save(out_file, image.format)

def _autorotate(image):
  exif = image._getexif()
  if exif:
    orientation_key = 274 # cf ExifTags
    if orientation_key in exif:
      orientation = exif[orientation_key]

      if orientation == 2:
        return image.transpose(Image.FLIP_LEFT_RIGHT)
      elif orientation == 3:
        return image.transpose(Image.ROTATE_180)
      elif orientation == 4:
        return image.transpose(Image.FLIP_TOP_BOTTOM)
      elif orientation == 5:
        return image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_90)
      elif orientation == 6:
        return image.transpose(Image.ROTATE_270)
      elif orientation == 7:
        return image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
      elif orientation == 8:
        return image.transpose(Image.ROTATE_90)

  return image