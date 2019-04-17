#!/usr/bin/env python3

from distutils.core import setup
from os import path

import file_sorter

if __name__ == '__main__':
    setup(
        name='file_sorter',
        description="Automatically assign files to directories in a smart way.",
        long_description=file_sorter.__doc__,
        version=file_sorter.__version__,
        author=file_sorter.__author__,
        license=file_sorter.__license__,
        packages=[],
        py_modules=['file_sorter'],
        scripts=[],
    )
