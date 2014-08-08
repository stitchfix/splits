import unittest
import tempfile
import shutil
import os

from splits import SplitReader, SplitWriter


class TestMultiReader(unittest.TestCase):

    def setUp(self):
        self.temp_dir_path = tempfile.mkdtemp()
        self.path = os.path.join(self.temp_dir_path, 'foo')
        os.makedirs(self.path)

        self.writer = SplitWriter(self.path, suffix='.txt', lines_per_file=2)
        self.writer.writelines([str(x) for x in range(0, 10)])
        self.writer.close()

        self.reader = SplitReader(self.path + '.manifest')

    def tearDown(self):
        self.reader.close()
        shutil.rmtree(self.temp_dir_path)

    def test_read_lines(self):
        lines = self.reader.readlines()

        self.assertEquals(len(lines), 10)
        for index, x in enumerate(lines):
            self.assertEquals(x, str(index))

    def test_read(self):
        lines = self.reader.read()

        self.assertEquals(len(lines.split('\n')), 10)
        for index, x in enumerate(lines.split('\n')):
            self.assertEquals(x, str(index))
