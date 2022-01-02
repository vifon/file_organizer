# File Organizer

*File Organizer* is a Python library that can be used to sort any kind of
files into relevant directories.

Each direct subdirectory of the target directory root is scored for
each file in the input directory as a possible candidate for
destination.  The primary score is the number of words the target
directory name contains that the source file name also contains (see
the example below, it'll be easier to understand this way).  The short
words are ignored, by default these below 3 characters.  If there are
multiple candidates with the same primary score, a secondary score is
used: the percentage of words in the target directory name that
appeared in the source file name.  Additionally targets designated
with the explicit rules are always scored 9999.

## Example

These are the results of running the [example script](https://github.com/vifon/file_organizer/blob/master/examples/book_organizer.py).

[![](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/1-input_files.png)](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/1-input_files.png)

[![](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/2-smart_matching.png)](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/2-smart_matching.png)

[![](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/3-preview.png)](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/3-preview.png)

[![](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/4-output_files.png)](https://raw.githubusercontent.com/vifon/file_organizer/master/examples/4-output_files.png)

## Copyright

Copyright (C) 2019-2022  Wojciech Siewierski

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
