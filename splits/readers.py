import copy

from splits.util import path_for_part

class SplitReader(object):
    def __init__(self, manifest_path_or_list,
                 fileClass=open,
                 fileArgs={'mode': 'r'}):
        self.fileClass = fileClass
        self.fileArgs = copy.deepcopy(fileArgs)

        if type(manifest_path_or_list) == list:
            self.manifest = manifest_path_or_list
        else:
            if not manifest_path_or_list.endswith('.manifest'):
                manifest_path_or_list += '.manifest'

            with self.fileClass(manifest_path_or_list, **self.fileArgs) as f:
                # remove newlines from filenames
                self.manifest = [x[:-1] for x in f.readlines()]

        self._lines = iter(self._get_lines())
        self._buf = ''

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __iter__(self):
        return self._get_lines()

    def close(self):
        pass

    def read(self, num=None):
        if num and num > 0:
            buf = ''
            while num > 0:
                try:
                    line = self._buf if self._buf else next(self._lines)
                except:
                    return ''

                if len(line) > num:
                    buf += line[:num]
                    self._buf = line[num:]
                    num = 0
                else:
                    buf += line
                    num -= len(line)
                    self._buf = ''

            return buf
        else:
            return ''.join(self.readlines())

    def readline(self, limit=None):
        try:
            line = self._buf if self._buf else next(self._lines)

            if limit and len(line) > limit:
                self._buf = line[limit:]
                return line[:limit]

            self._buf = ''
            return line
        except:
            return ''

    def readlines(self):
        return list(self._lines)

    def _get_lines(self):
        for path in self.manifest:
            f = self.fileClass(path, **self.fileArgs)
            for line in f.readlines():
                yield line
            f.close()
