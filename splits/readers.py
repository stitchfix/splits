

class SplitReader(object):
    def __init__(self,
                 manifest_path_or_list,
                 fileClass=open,
                 fileArgs={'mode': 'rb'}):
        self.fileClass = fileClass
        self.fileArgs = fileArgs

        if type(manifest_path_or_list) == list:
            self.manifest = iter(self._get_files(manifest_path_or_list))
        else:
            if not manifest_path_or_list.endswith('.manifest'):
                manifest_path_or_list += '.manifest'

            with self.fileClass(manifest_path_or_list, **self.fileArgs) as f:
                # remove newlines from filenames
                self.manifest = iter(
                    self._get_files([x[:-1] for x in f.readlines()]))

        self._current_file = next(self.manifest)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        line = self.readline()
        if line:
            return line
        raise StopIteration()

    def close(self):
        pass

    def read(self, num=None):
        val = b''

        if num is None:
            num = 0

        try:
            while True:
                if num > 0:
                    new_data = self._get_current_file().read(num - len(val))
                else:
                    new_data = self._get_current_file().read()

                if not new_data:
                    self._current_file.close()
                else:
                    val += new_data

                if num > 0 and len(val) == num:
                    break
        except StopIteration:
            pass

        return val

    def readline(self, limit=None):
        line = b''

        if limit is None:
            limit = 0

        try:
            while True:
                if limit > 0:
                    new_data = self._get_current_file().readline(
                        limit - len(line))
                else:
                    new_data = self._get_current_file().readline()

                if not new_data:
                    self._current_file.close()
                else:
                    line += new_data

                if limit > 0 and len(line) == limit:
                    break
                elif line.endswith(b'\n'):
                    break
        except StopIteration:
            pass

        return line

    def readlines(self, sizehint=None):
        all_lines = []
        line = self.readline()

        while line:
            all_lines.append(line)
            line = self.readline()

        return all_lines

    def _get_current_file(self):
        if self._current_file.closed:
            self._current_file = next(self.manifest)

        return self._current_file

    def _get_files(self, manifest):
        for path in manifest:
            f = self.fileClass(path, **self.fileArgs)
            yield f
            f.close()
