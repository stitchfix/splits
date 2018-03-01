# Splits

Splits is a library for reading and writing files in splittable chunks.
It works on any file-like object.
There is built in support for writing and reading split files from S3.
It also has built in support for gzip.

## Installation

```
  $ pip install splits
```

## Usage

```python
from splits import SplitWriter, SplitReader
from splits.s3 import S3File, GzipS3File

if __name__ == '__main__':

    with SplitWriter('s3://test-bucket/test-multifile',
                     suffix='.txt', lines_per_file=100,
                     fileClass=GzipS3File) as w:
        w.writelines([str(x) for x in range(0, 1000)])

    with SplitReader('s3://test-bucket/test-multifile',
                     fileClass=GzipS3File) as r:
        for line in r:
            print line

```

## Tests

```
 $ pip install tox
```

To run the tests in both Python2 and Python3 run,

```
 $ tox
```
