#!/usr/bin/env python3

from distutils.core import setup
from os import path

import file_organizer

if __name__ == '__main__':
    setup(
        name='file_organizer',
        description="Automatically assign files to directories in a smart way.",
        long_description=file_organizer.__doc__,
        version=file_organizer.__version__,
        author=file_organizer.__author__,
        license=file_organizer.__license__,
        packages=['file_organizer'],
        py_modules=[],
        scripts=[],
    )
