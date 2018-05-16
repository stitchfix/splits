import six
import gzip
import boto.s3
import boto.s3.connection
import boto.provider
import zipfile
import six.moves.urllib as urllib
from itertools import groupby


def is_s3_uri(uri):
    uri = str(uri)
    return uri.startswith('s3://') or uri.startswith('s3n://')

class S3Uri(object):

    def __init__(self, uri):
        uri = str(uri)
        assert is_s3_uri(uri), "Invalid S3 uri - '{0}'".format(uri)
        self._parseresult = urllib.parse.urlparse(uri)

    @property
    def bucket(self):
        return self._parseresult.netloc

    @property
    def path(self):
        p = self._parseresult.path
        if p.startswith('/'):
            p = p[1:]
        return p

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
    aws_settings_provider = None

    def __init__(self, region='us-east-1'):
        # use a single provider to avoid NoAuthHandler exceptions
        # see: http://blog.johnryding.com/post/122337566993/solving-intermittent-noauthhandlerfound-errors-in
        if S3.aws_settings_provider is None:
            S3.aws_settings_provider = boto.provider.Provider('aws')

        self._conn = boto.s3.connect_to_region(
            region,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
            provider=S3.aws_settings_provider
        )

    @property
    def access_key(self):
        return self._conn.access_key

    @property
    def secret_key(self):
        return self._conn.secret_key

    @property
    def security_token(self):
        return self._conn.provider.security_token

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

    def get_key(self, uri):
        uri = S3Uri(uri)
        assert uri.is_file()
        return self._conn.get_bucket(uri.bucket)\
                         .get_key(uri.path)

    def putfile(self, file, uri):
        uri = S3Uri(uri)
        assert uri.is_file()
        self._conn.get_bucket(uri.bucket)\
                  .new_key(uri.path)\
                  .set_contents_from_file(file, rewind=True)

    def getfile(self, uri, file):
        uri = S3Uri(uri)
        assert uri.is_file()
        self._conn.get_bucket(uri.bucket)\
                  .new_key(uri.path)\
                  .get_contents_to_file(file)

    def getstring(self, uri):
        uri = S3Uri(uri)
        assert uri.is_file()
        return self._conn.get_bucket(uri.bucket).new_key(uri.path).get_contents_as_string()

    def putstring(self, string, uri):
        uri = S3Uri(uri)
        assert uri.is_file()
        self._conn.get_bucket(uri.bucket).new_key(uri.path).set_contents_from_string(string)

    def rm(self, uris):
        uris = [S3Uri(uri) for uri in uris]

        for bucket, group in groupby(
            sorted(uris, key=lambda uri: uri.bucket), lambda i: i.bucket):
                returned_keys = self._conn.get_bucket(bucket)\
                                    .delete_keys(
                                        boto.s3.key.Key(bucket, i.path) for i in group)

                if(len(returned_keys.errors) > 0):
                    raise IOError('Could not delete keys: {keys}'.format(
                        keys=[k for k in returned_keys.errors]))

class S3File(six.BytesIO, object):
    s3 = None

    def __init__(self, uri, mode='r', s3 = None):
        self.mode = mode
        self.s3uri = S3Uri(uri)
        assert self.s3uri.is_file(), "Uri (got {0}) must be a file (not directory or bucket) on S3.".format(uri)
        if s3:
            self.s3 = s3
        else:
            self.__init_s3()
        six.BytesIO.__init__(self)

        if 'r' in self.mode:
            self.s3.getfile(self.s3uri, self)
            self.seek(0)

    def __init_s3(cls):
        if not cls.s3:
            cls.s3 = S3()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    if six.PY3:
        def write(self, data):
            if isinstance(data, six.string_types):
                data = data.encode()
            super(S3File, self).write(data)

    def close(self):
        if 'w' in self.mode:
            self.flush()
            self.s3.putfile(self, self.s3uri)

class GzipS3File(gzip.GzipFile):
    def __init__(self, uri, *args, **kwargs):
        mode = kwargs['mode'] if 'mode' in kwargs else 'rb'
        s3 = kwargs['s3'] if 's3' in kwargs else None
        self.s3File = S3File(uri, mode=mode, s3=s3)
        super(GzipS3File, self).__init__(fileobj=self.s3File, mode=mode)

    def close(self):
        super(GzipS3File, self).close()
        self.s3File.close()

    if six.PY3:
        def write(self, data):
            if isinstance(data, six.string_types):
                data = data.encode()
            super(GzipS3File, self).write(data)
