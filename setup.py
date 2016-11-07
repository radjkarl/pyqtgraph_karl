# coding=utf-8
"""
usage:
 (sudo) python setup.py +
     install        ... local
     register       ... at http://pypi.python.org/pypi
     sdist          ... create *.tar to be uploaded to pyPI
     sdist upload   ... build the package and upload in to pyPI
"""

import pyqtgraph_karl
from fancytools.os.setup import setup
import sys

setup(pyqtgraph_karl)
