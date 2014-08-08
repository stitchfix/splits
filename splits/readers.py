import copy

from splits.util import path_for_part


class SplitReader(object):
    def __init__(self, manifest_path,
                 fileClass=open,
                 fileArgs={'mode': 'r'}):
        self.fileClass = fileClass
        self.fileArgs = copy.deepcopy(fileArgs)

        if not manifest_path.endswith('.manifest'):
            manifest_path += '.manifest'

        with self.fileClass(manifest_path, **self.fileArgs) as f:
            # remove newlines from filenames
            self.manifest = [x[:-1] for x in f.readlines()]

        self._lines = iter(self._get_lines())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __iter__(self):
        return self._get_lines()

    def close(self):
        pass

    def read(self):
        return '\n'.join(self.readlines())

    def readlines(self):
        return list(self._lines)

    def _get_lines(self):
        for path in self.manifest:
            f = self.fileClass(path, **self.fileArgs)
            for line in f.readlines():
                yield line[:-1]
            f.close()
