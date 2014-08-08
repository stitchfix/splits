import StringIO
import gzip
import boto.s3
import urlparse


def is_s3_uri(uri):
    uri = str(uri)
    return uri.startswith('s3://') or uri.startswith('s3n://')


class S3Uri(object):

    def __init__(self, uri):
        uri = str(uri)
        assert is_s3_uri(uri), "Invalid S3 uri - '{0}'".format(uri)
        self._parseresult = urlparse.urlparse(uri)

    @property
    def bucket(self):
        return self._parseresult.netloc

    @property
    def path(self):
        return self._parseresult.path

    @property
    def name(self):
        return self._parseresult.geturl()

    @property
    def type(self):
        return self.is_file() and "file" or "dir"

    def is_file(self):
        return len(self.path) and not self.path.endswith('/')

    def __str__(self):
        return self.name


class S3(object):

    def __init__(self, region='us-east-1'):
        self._conn = boto.s3.connect_to_region(region)

    @property
    def access_key(self):
        return self._conn.access_key

    @property
    def secret_key(self):
        return self._conn.secret_key

    def _list_prefix(self, s3uri):
        results = self._conn.get_bucket(s3uri.bucket).list(s3uri.path, delimiter='/')
        return (S3Uri('s3://{0}/{1}'.format(s3uri.bucket, i.name)) for i in results)

    def _list_buckets(self):
        return (S3Uri('s3://{0}'.format(i.name)) for i in self._conn.get_all_buckets())

    def ls(self, uri=None):
        if uri:
            s3uri = S3Uri(uri)
            return self._list_prefix(s3uri)
        return self._list_buckets()

    def putfile(self, file, uri):
        if not isinstance(uri, S3Uri):
            uri = S3Uri(uri)
        assert uri.is_file()
        self._conn.get_bucket(uri.bucket)\
                  .new_key(uri.path)\
                  .set_contents_from_file(file, rewind=True)

    def getfile(self, uri, file):
        if not isinstance(uri, S3Uri):
            uri = S3Uri(uri)

        assert uri.is_file()
        self._conn.get_bucket(uri.bucket)\
                  .new_key(uri.path)\
                  .get_contents_to_file(file)


class S3File(StringIO.StringIO):
    s3 = S3()

    def __init__(self, uri, mode='r'):
        self.mode = mode
        self.s3uri = S3Uri(uri)
        assert self.s3uri.is_file(), "Uri (got {0}) must be a file (not directory or bucket) on S3.".format(self.uri)
        StringIO.StringIO.__init__(self)

        if self.mode == 'r':
            self.s3.getfile(self.s3uri, self)
            self.seek(0)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self.mode == 'w':
            self.flush()
            self.s3.putfile(self, self.s3uri)


class GzipS3File(gzip.GzipFile):
    def __init__(self, uri, *args, **kwargs):
        mode = kwargs['mode'] if 'mode' in kwargs else 'r'
        self.s3File = S3File(uri, mode=mode)
        super(GzipS3File, self).__init__(fileobj=self.s3File, mode=mode)

    def close(self):
        super(GzipS3File, self).close()
        self.s3File.close()
