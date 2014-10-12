__author__ = 'jevgenik'

import os, shutil
import pkg_resources
from string import Template
from os.path import join as path_join, dirname
from glob import glob
from PIL import Image
import cgi


class Gallery:
  def __init__(self, gallery_dir, photo_dir):
    self.path = gallery_dir
    self.index_path = path_join(self.path, 'index.html')
    self.photo_path = path_join(self.path, 'photos')
    self.thumbs_path = path_join(self.path, 'thumbs')
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
      image = Image.open(path_join(self.photo_path, image_file))
      image.thumbnail(self.thumb_size, Image.ANTIALIAS)

      thumb = Image.new('RGBA', self.thumb_size, (255, 255, 255, 0))
      thumb.paste(
          image,
          ((self.thumb_size[0] - image.size[0]) / 2, (self.thumb_size[1] - image.size[1]) / 2))

      thumb_file = path_join(self.thumbs_path, image_file)
      dir = dirname(thumb_file)
      if not os.path.exists(dir):
        print "Creating dir:", dir
        os.makedirs(dir)
      thumb.save(thumb_file, image.format)

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
      html += '<a href="%s"><img src="%s"></a>' % (cgi.escape('photos/' + image_file), cgi.escape('thumbs/' + image_file))

    tpl = Template(open(pkg_resources.resource_filename(__name__, path_join("data", "template.html"))).read())
    content = tpl.substitute({"images": html})
    open(self.index_path, 'w').write(content)

    print "Index created"


  def _scan_photo_path(self):
    if hasattr(self, 'images'):
      return

    old_cwd = os.getcwd()
    os.chdir(self.photo_path)
    self.images = glob('*.jpg')

    os.chdir(old_cwd)