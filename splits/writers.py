import os
import copy

from splits.util import path_for_part


class SplitWriter(object):
    def __init__(self, basepath,
                 suffix='',
                 lines_per_file=100000,
                 fileClass=open,
                 fileArgs={'mode': 'w'}):
        self.suffix = suffix
        self.basepath = basepath
        self.lines_per_file = lines_per_file
        self.fileClass = fileClass
        self.fileArgs = copy.deepcopy(fileArgs)
        self._seqnum = 0
        self._linenum = 0
        self._filelinenum = 0
        self._written_file_paths = []
        self._current_file = self._create_file()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def write(self, data):
        for line in data.split('\n'):
            self._write_line(line)

    def writelines(self, lines):
        for line in lines:
            self._write_line(line)

    def _write_line(self, line):
        f = self._get_current_file()
        f.write(line + '\n')
        self._linenum += 1
        self._filelinenum += 1

    def close(self):
        if self._current_file:
            self._current_file.close()

        path = self.basepath[:-1] if self.basepath.endswith('/') else self.basepath
        path += '.manifest'

        f = self.fileClass(path, **self.fileArgs)
        f.write(''.join([x + '\n' for x in self._written_file_paths]))
        f.close()

    def _get_current_file(self):
        if self._filelinenum >= self.lines_per_file:

            if self._current_file:
                self._current_file.close()

            self._current_file = self._create_file()

        return self._current_file

    def _create_file(self):
        self._seqnum += 1
        self._filelinenum = 0
        path = path_for_part(self.basepath, self._seqnum, self.suffix)
        self._written_file_paths.append(path)
        return self.fileClass(path, **self.fileArgs)
