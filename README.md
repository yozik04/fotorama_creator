Fotorama creator
================

Fotorama image gallery creator.

Creates thumbnails and scaled down images for optimal web performance.

Script uses all cpu threads available to scale images down with ultimate performance.

Additionally supports:

* Importing only Google's Picasa starred images.
* Sorting by date and file name (date is by default)

Installation
=============

    git clone git@github.com:yozik04/fotorama_creator.git
    cd fotorama_creator
    sudo ./setup.py install

sudo is not required if you are installing into virtualenv

Usage
======
Example:

    fotorama_create ~/a/picture/folder

All available options:

    usage: fotorama_create [-h] [-o OUTPUT_DIR] [-t TITLE] [-s {date,name}] [-ps]
                       photo_dir

    Create photo gallery in current directory.
    
    positional arguments:
      photo_dir             Source photo directory
    
    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                            Current working directory is used by default
      -t TITLE, --title TITLE
                            Gallery title to be used in index.html
      -s {date,name}, --sort {date,name}
                            Sort pictures by
      -ps, --picasa_star    Only Picasa starred photos
      
Results
========
After processing your folder will look like:

    ├── index.html
    ├── optimized
    │   ├── a.JPG
    │   └── b.JPG
    ├── photos -> ~/a/picture/folder
    ├── static
    │   ├── fotorama.css
    │   ├── fotorama.js
    │   ├── fotorama.png
    │   ├── fotorama@2x.png
    │   └── jquery-1.10.2.min.js
    └── thumbs
        ├── a.JPG
        └── b.JPG
        
index.html was generated for your image gallery.
Open it in a browser to see your gallery locally.

Your source images folder is left untouched!

TODO
=====
* Create map links if images have coordinates.
* Enable original image download.
* Import image titles from Google Picasa.