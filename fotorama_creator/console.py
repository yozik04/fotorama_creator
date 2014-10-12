#!/usr/bin/env python
from __future__ import print_function
__author__ = 'jevgenik'

import os, sys

def main():
  import argparse

  class readable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
      prospective_dir=values
      if not os.path.isdir(prospective_dir):
        raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid dir".format(prospective_dir))

      if os.access(prospective_dir, os.R_OK):
        setattr(namespace,self.dest,prospective_dir)
      else:
        raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

  class writable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
      prospective_dir=values
      if not os.path.isdir(prospective_dir):
        raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid dir".format(prospective_dir))

      if os.access(prospective_dir, os.W_OK):
        setattr(namespace,self.dest,prospective_dir)
      else:
        raise argparse.ArgumentTypeError("readable_dir:{0} is not a writable dir".format(prospective_dir))

  parser = argparse.ArgumentParser(description='Create photo gallery in current directory.', fromfile_prefix_chars="@")
  parser.add_argument('photo_dir', action=readable_dir, help="Source photo directory")
  parser.add_argument('-o', '--output_dir', action=writable_dir, default=os.getcwd(), help="Current working directory is used by default")
  parser.add_argument('-t', '--title', type=str, default="My fotorama gallery", help="Gallery title to be used in index.html")
  parser.add_argument('-s', '--sort', type=str, default="date", choices=['date', 'name'], help="Sort pictures by")

  try:
    args = parser.parse_args()
  except argparse.ArgumentTypeError as e:
    print(e.message, file=sys.stderr)

  from fotorama_creator.gallery import Gallery
  g = Gallery(**vars(args))
  g.create()

if __name__ == "__main__":
  main()