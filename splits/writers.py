import os

from splits.util import path_for_part


class SplitWriter(object):
    def __init__(self, basepath,
                 suffix='',
                 lines_per_file=100000,
                 fileClass=open,
                 fileArgs={'mode': 'wb'}):
        self.suffix = suffix
        self.basepath = basepath
        self.lines_per_file = lines_per_file
        self.fileClass = fileClass
        self.fileArgs = fileArgs
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
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        cnt = data.count(b'\n')
        for index, line in enumerate(data.split(b'\n')):
            if index == cnt:
                self._write_line(line)
            else:
                self._write_line(line + b'\n')

    def writelines(self, lines):
        for line in lines:
            if not isinstance(line, bytes):
                line = line.encode('utf-8')
            self._write_line(line)

    def _write_line(self, line):
        f = self._get_current_file()
        f.write(line)
        self._linenum += line.count(b'\n')
        self._filelinenum += line.count(b'\n')

    def close(self):
        if self._current_file:
            self._current_file.close()

        path = self.basepath[:-1] if self.basepath.endswith('/') else self.basepath
        path += '.manifest'

        f = self.fileClass(path, **self.fileArgs)
        f.write(b''.join([x + b'\n' for x in self._written_file_paths]))
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
        self._written_file_paths.append(path.encode('utf-8'))
        return self.fileClass(path, **self.fileArgs)
