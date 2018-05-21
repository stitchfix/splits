import unittest
import tempfile
import shutil
import os

from context import SplitWriter


def stringify(intval, skip_nl):
    newline = '\n' if not skip_nl else ''
    return (str(intval) + newline).encode("utf-8")


class TestMultiWriter(unittest.TestCase):

    def setUp(self):
        self.temp_dir_path = tempfile.mkdtemp()
        self.path = os.path.join(self.temp_dir_path, 'foo')
        os.makedirs(self.path)
        self.writer = SplitWriter(self.path, suffix='.txt',
                                  lines_per_file=2, fileClass=open)

    def tearDown(self):
        self.writer.close()
        shutil.rmtree(self.temp_dir_path)

    def fileExists(self, part_path):
        path = os.path.join(self.path, part_path)
        return os.path.isfile(path)

    def test_writes_correct_number_of_files(self):
        self.writer.write(b'\n'.join([stringify(x, True) for x in range(0, 10)]))

        for i in range(1, 6):
            self.assertTrue(self.fileExists('%06d.txt' % i))

        self.assertFalse(self.fileExists('%06d.txt' % 6))

    def test_writes_correct_number_of_files_str(self):
        self.writer.write('\n'.join(["ln{}".format(x) for x in range(0, 10)]))

        for i in range(1, 6):
            self.assertTrue(self.fileExists('%06d.txt' % i))

        self.assertFalse(self.fileExists('%06d.txt' % 6))

    def test_writes_correct_number_of_files_with_writelines(self):
        self.writer.writelines([stringify(x, x == 9) for x in range(0, 10)])

        for i in range(1, 6):
            self.assertTrue(self.fileExists('%06d.txt' % i))

        self.assertFalse(self.fileExists('%06d.txt' % 6))

    def test_writes_odd_number_of_lines(self):
        self.writer.writelines([stringify(x, x == 10) for x in range(0, 11)])

        for i in range(1, 7):
            self.assertTrue(self.fileExists('%06d.txt' % i))

        self.assertFalse(self.fileExists('%06d.txt' % 7))


if __name__ == "__main__":
    unittest.main()
