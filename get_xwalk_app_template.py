#!/usr/bin/env python

# Copyright (c) 2013 Intel Corporation. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Retrieves the latest xwalk application template build version number, gets the
latest xwalk application template package and extracts it to the
destination directory.

Sample usage from shell script:
python get_xwalk_app_template.py --dest_dir=/hangonman/android
"""
import gzip
import optparse
import os
import shutil
import sys
import tarfile
import urllib2
import urlparse

from urllib2 import urlopen


class GetXWalkAppTemplate(object):
  """ The class is used to retrieve the latest xwalk application template
  build version number and get the url address of the latest xwalk application
  template and provide the interfaces of getting the packed file and extracting
  the corresponding package.

  Args:
    url: The latest url of indicating the xwalk application template version
        number.
    file_name: The file name of the xwalk application template package name.
  """
  def __init__(self, url, file_name):
    self.url = url
    self.file_name = file_name
    try:
      self.updated_url = self.__get_url_addr()
    except URLError:
      raise Exception('Error in network connection to dev-wrt-android-build'
                      'server.')
    except HTTPError:
      raise Exception('Error in the response from dev-wrt-android-build'
                      'server.')

  def __get_url_addr(self):
    """ Get the latest version url address of xwalk application template, it
    is an internally called function.

    Gets the latest version number of xwalk application template, retrieves
    the url address of the latest version based on the version number, locates
    the file of packed xwalk application template and returns the corresponding
    url address.

    Returns:
      The latest version url address of xwalk application template.
    """
    request = urlopen(self.url)
    version = request.readline()
    request.close()
    request = urlparse.urlparse(self.url)
    unparsed_url = urlparse.urlunparse((request.scheme, request.netloc,
                                       request.path, '', '', ''))
    updated_url = urlparse.urljoin(unparsed_url, version + '/' +
                                   self.file_name)
    return updated_url

  def __get_packed_xwalk_app_template(self, dest_dir):
    """ Gets the corresponding packed file of the latest version number,
    it is an internally called function.
    """
    input_file = urllib2.urlopen(self.updated_url)
    contents = input_file.read()
    input_file.close()
    file_path = os.path.join(dest_dir, self.file_name)
    if os.path.isfile(file_path):
      os.remove(file_path)
    file_dir = dest_dir + '/' + self.file_name.split('.tar.gz')[0]
    if os.path.exists(file_dir):
      shutil.rmtree(file_dir)
    output_file = open(file_path, 'w')
    output_file.write(contents)
    output_file.close()

  def ExtractFile(self, dest_dir):
    """ Extracts the corresponding file of the latest version number.
    """
    self.__get_packed_xwalk_app_template(dest_dir)
    file_path = os.path.join(dest_dir, self.file_name)
    tar = tarfile.open(file_path, 'r:gz')
    tar.extractall(dest_dir)
    tar.close()
    file_path = os.path.join(dest_dir, self.file_name)
    if os.path.isfile(file_path):
      os.remove(file_path)


def main():
  """Responds to command mode and get the latest xwalk application template
  build version."""
  parser = optparse.OptionParser()
  info = ('The input json-format file name. Such as: '
          '--dest_dir=/hangonman/android')
  parser.add_option('-d', '--dest_dir', action='store', dest='dest_dir',
                    help=info)
  opts, _ = parser.parse_args()
  if not os.path.exists(opts.dest_dir):
    print 'Destination directory is not existed!'
    return 1
  latest_url = ('http://wrt-build.sh.intel.com/archive/'
               'snapshots/dev-wrt-android-build/LATEST')
  file_name = 'xwalk_app_template.tar.gz'
  app_template_handler = GetXWalkAppTemplate(latest_url, file_name)
  try:
    app_template_handler.ExtractFile(opts.dest_dir)
  except tarfile.TarError:
    raise Exception('Error in the process of tar file.')
  return 0


if __name__ == '__main__':
  sys.exit(main())
