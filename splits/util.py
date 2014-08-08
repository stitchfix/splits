import os


def path_for_part(basepath, seqnum, suffix):
    return os.path.join(basepath, '%06d%s' % (seqnum, suffix))
