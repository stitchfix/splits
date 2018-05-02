import unittest
import tempfile
import shutil
import os

from context import SplitReader, SplitWriter


def stringify(intval, skip_nl):
    newline = '\n' if not skip_nl else ''
    return (str(intval) + newline).encode("utf-8")


class TestMultiReader(unittest.TestCase):

    def setUp(self):
        self.temp_dir_path = tempfile.mkdtemp()
        self.path = os.path.join(self.temp_dir_path, 'foo')
        os.makedirs(self.path)

        self.writer = SplitWriter(self.path, suffix='.txt', lines_per_file=2)
        #self.writer.writelines(b'\n'.join([str(x).encode("utf-8") for x in range(0, 10)]))
        self.writer.writelines([stringify(x, x == 9) for x in range(0, 10)])
        self.writer.close()

        self.reader = SplitReader(self.path + '.manifest')

    def tearDown(self):
        self.reader.close()
        shutil.rmtree(self.temp_dir_path)

    def test_read(self):
        lines = self.reader.read()

        self.assertEqual(len(lines.split(b'\n')), 10)
        for index, x in enumerate(lines.split(b'\n')):
            self.assertEqual(x, str(index).encode('utf-8'))

    def test_read_n_chars(self):
        for index in range(0, 19):
            char = self.reader.read(1)
            if index % 2 == 0:
                self.assertEqual(char, str(index // 2).encode('utf-8'))
            else:
                self.assertEqual(char, b'\n')

        self.assertEqual(self.reader.read(1), b'')

    def test_read_n_chars(self):
        chars = self.reader.read(11)
        self.assertEqual(chars, b'0\n1\n2\n3\n4\n5')

    def test_readlines(self):
        lines = self.reader.readlines()
        self.assertEqual(len(lines), 10)

    def test_read_line_n_chars(self):
        line = self.reader.readline(1)
        self.assertEqual(b'0', line)
        line = self.reader.readline()
        self.assertEqual(b'\n', line)
        line = self.reader.readline()
        self.assertEqual(b'1\n', line)
        line = self.reader.readline(2)
        self.assertEqual(b'2\n', line)
        line = self.reader.readline()
        self.assertEqual(b'3\n', line)

    def test_reader_is_iterator(self):
        count = 0
        for line in self.reader:
            count += 1

        self.assertEqual(count, 10)

    def test_manual_manifest(self):
        manifest = [os.path.join(self.path, '%06d%s' % (x, '.txt'))
                    for x in range(1,6)]

        self.reader = SplitReader(manifest)
        lines = self.reader.read()

        self.assertEqual(len(lines.split(b'\n')), 10)
        for index, x in enumerate(lines.split(b'\n')):
            self.assertEqual(x, str(index).encode('utf-8'))

    def test_manual_subset_manifest(self):
        manifest = [os.path.join(self.path, '%06d%s' % (x, '.txt'))
                    for x in range(1,4)]

        self.reader = SplitReader(manifest)
        lines = self.reader.read()

        self.assertEqual(len(lines.split(b'\n')[:-1]), 6)
        for index, x in enumerate(lines.split(b'\n')[:-1]):
            self.assertEqual(x, str(index).encode('utf-8'))
