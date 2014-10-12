#!/usr/bin/env python
from setuptools import setup, find_packages
import pkg_resources

install_requires=[]

def package_installed(pkg):
    """Check if package is installed"""
    req = pkg_resources.Requirement.parse(pkg)
    try:
        pkg_resources.get_provider(req)
    except pkg_resources.DistributionNotFound:
        return False
    else:
        return True

# depend in Pillow if it is installed, otherwise
# depend on PIL if it is installed, otherwise
# require Pillow
if package_installed('Pillow'):
    install_requires.append('Pillow !=2.4.0')
elif package_installed('PIL'):
    install_requires.append('PIL>=1.1.6,<1.2.99')
else:
    install_requires.append('Pillow !=2.4.0')

setup(
  name='fotorama_creator',
  version='0.0.1',
  packages=find_packages(),
  include_package_data=True,
  entry_points = {
    'console_scripts': ['fotorama_create = fotorama_creator.console:main']
  },
  url='https://github.com/yozik04/fotorama_creator',
  license='MIT',
  author='Jevgeni Kiski',
  author_email='yozik04@gmail.com',
  description='Fotorama image gallery creator',
  zip_safe=False,
  install_requires=install_requires
)