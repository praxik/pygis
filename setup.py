import setuptools

def readme():
  with open( 'README.rst', 'r' ) as f:
    return f.read()

setuptools.setup(
  name = 'pygis',
  version = '0.0.1',
  author = 'Joshua Koch',
  author_email = 'joshua.b.koch@gmail.com',
  url = 'https://github.com/praxik/pygis',
  description = '',
  long_description = readme(),
  long_description_content_type = 'text/markdown',
  license = 'Apache',
  packages = setuptools.find_packages(),
  install_requires = [
    'fiona >= 3.12',
    'shapely >= 0.6' ],
  classifiers = [
    'Programming Lanuguage :: Python :: 3.6',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent' ] )
