#!/usr/bin/python -O
# mining/populate/insertRuns.py.  Generated from insertRuns.py.in by configure.

from itertools import imap
from optparse import OptionParser
from os import makedirs, rename, stat
from os.path import basename, dirname, exists
from time import gmtime, strftime
import sys

from common import Upload, connect, results


columns = {
    'HTTP_SAMPLER_APPLICATION_NAME': 'application_name',
    'HTTP_SAMPLER_APPLICATION_VERSION': 'application_version',
    'HTTP_SAMPLER_APPLICATION_RELEASE': 'application_release',
    'HTTP_SAMPLER_BUILD_DISTRIBUTION': 'build_distribution',
    'HTTP_SAMPLER_VERSION': 'version',
    'HTTP_SAMPLER_SPARSITY': 'sparsity',
    'HTTP_SAMPLER_EXIT_SIGNAL': 'exit_signal',
    'HTTP_SAMPLER_EXIT_STATUS': 'exit_status',
    'DATE': 'date',
    'SERVER_NAME': 'server_name',
    }


servers = {
    '/afs/cs.wisc.edu/p/cbi/uploads/www.cs.wisc.edu': 'www.cs.wisc.edu',
    '/afs/cs.wisc.edu/p/cbi/uploads/cbi.cs.wisc.edu': 'cbi.cs.wisc.edu',
    '/afs/cs.wisc.edu/p/cbi/uploads/sampler.cs.berkeley.edu': 'sampler.cs.berkeley.edu',
    '/afs/cs.stanford.edu/group/cbi/www/sampler-uploads': 'www.cs.stanford.edu',
    }


archives = {
    'www.cs.wisc.edu': '/afs/cs.wisc.edu/p/cbi/uploads/www.cs.wisc.edu/archive',
    'cbi.cs.wisc.edu': '/afs/cs.wisc.edu/p/cbi/uploads/cbi.cs.wisc.edu/archive',
    'sampler.cs.berkeley.edu': '/afs/cs.wisc.edu/p/cbi/uploads/berkeley/archive',
    'www.cs.stanford.edu': '/afs/cs.stanford.edu/group/cbi/www/archive'
    }


def readEnvironment(environPath):
    items = file(environPath)
    items = imap(str.rstrip, items)
    items = ( item.split('\t') for item in items )
    return dict(items)


class MalformedRun(StandardError):

    __slots__ = ['run']

    def __init__(self, run, reason):
        StandardError.__init__(self, reason)
        self.run = run


class Run(object):

    __fields = ['run_id', 'application_name', 'application_version', 'application_release', 'build_distribution', 'version', 'sparsity', 'exit_signal', 'exit_status', 'date', 'server_name']
    __slots__ = __fields + ['subdir']

    def __init__(self, subdir):
        self.subdir = subdir
        self.run_id = basename(subdir)

        environPath = '%s/environment' % subdir
        environment = readEnvironment(environPath)
        for name, value in environment.iteritems():
            if name in columns:
                setattr(self, columns[name], value)

        if not hasattr(self, 'build_distribution'):
            self.build_distribution = self.__guessDistro(environment)

        if self.build_distribution == 'fedora-4-noarch':
            self.build_distribution = 'fedora-4-i386'

        if not hasattr(self, 'version'):
            self.version = self.__guessVersion(environment)

        if not hasattr(self, 'date'):
            self.date = self.__guessDate(environPath)

        if not hasattr(self, 'server_name'):
            self.server_name = self.__guessServer(environPath)

        for slot in self.__slots__:
            problem = False
            if not hasattr(self, slot):
                problem = True
                print 'error: %s: missing attribute "%s"' % (subdir, slot)
            if problem:
                sys.exit(1)

        self.sparsity = int(self.sparsity)
        self.exit_signal = int(self.exit_signal)
        self.exit_status = int(self.exit_status)


    def __guessDistro(self, environment):
        instrumentor = environment.get('HTTP_SAMPLER_INSTRUMENTOR_VERSION')
        if instrumentor == '0.9.1': return 'fedora-1-i386'
        return 'redhat-9-i386'


    def __guessVersion(self, environment):
        guess = environment.get('HTTP_SAMPLER_INSTRUMENTOR_VERSION')
        if guess: return guess
        guess = environment.get('HTTP_SAMPLER_INSTRUMENTATION_VERSION')
        if guess: return guess
        self.__malformed('cannot guess version')


    def __guessDate(self, environPath):
        status = stat(environPath)
        return strftime('%F %T', gmtime(status.st_mtime))


    def __guessServer(self, environPath):
        prefix = environPath
        while prefix != '/':
            if prefix in servers:
                return servers[prefix]
            else:
                prefix = dirname(prefix)

        self.__malformed('cannot guess server')


    def __malformed(self, reason):
        raise MalformedRun(self, reason)


    def row(self):
        return [ getattr(self, field) for field in self.__fields ]


def uploadRuns(db, subdirs):
    upload = Upload(db, 'upload_run')

    def uploadRun(subdir):
        print 'upload:', subdir
        try:
            run = Run(subdir)
            row = run.row()
            upload.append(row)
            return run
        except MalformedRun, error:
            print 'error: %s: %s' % (subdir, error)
            return None

    runs = filter(bool, imap(uploadRun, subdirs))
    print 'uploading %d runs' % len(runs)
    upload.commit()
    print '\tdone'
    return runs


def main():
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-n', '--dry-run', action='store_true', default=False,
                      help='show what would be inserted without actually doing it')
    options, args = parser.parse_args()

    # temporary table to receive new runs
    db = connect()
    db.autocommit = False

    #cursor = db.cursor()
    #cursor.execute('SELECT run_id FROM run_suppress UNION SELECT run_id FROM run')
    #known = frozenset(row[0] for row in results(cursor))
    #print 'known:', len(known)
    #del cursor
    #return 13

    db.cursor().execute("""
      CREATE TEMPORARY TABLE upload_run (
          run_id VARCHAR(24) PRIMARY KEY NOT NULL,
          application_name VARCHAR(50) NOT NULL,
          application_version VARCHAR(50) NOT NULL,
          application_release VARCHAR(50) NOT NULL,
          build_distribution VARCHAR(50) NOT NULL,
          version VARCHAR(255) NOT NULL,
          sparsity INTEGER NOT NULL CHECK (sparsity > 0),
          exit_signal SMALLINT NOT NULL CHECK (exit_signal >= 0),
          exit_status SMALLINT NOT NULL CHECK (exit_status >= 0),
          CHECK (exit_status = 0 OR exit_signal = 0),
          date TIMESTAMP NOT NULL,
          server_name VARCHAR(50) NOT NULL
      )
      """)

    if args:
        subdirs = args
    else:
        subdirs = sys.stdin
        subdirs = imap(str.rstrip, subdirs)

    # upload new runs into temporary table
    subdirs = imap(dirname, subdirs)
    runs = uploadRuns(db, subdirs)

    # remove anything we already knew about
    print 'discard already-known runs'
    cursor = db.cursor()
    cursor.execute("""
      DELETE FROM upload_run
        USING run
        WHERE upload_run.run_id = run.run_id
    """)
    print '\t%d discarded' % cursor.rowcount
    del cursor

    # merge new runs into main table
    db.cursor().execute("""
      INSERT INTO run SELECT
          run_id,
          build_id,
          version,
          sparsity,
          exit_signal,
          exit_status,
          date,
          server_name
      FROM upload_run
      NATURAL LEFT JOIN build
    """)

    # finish up with database
    if options.dry_run:
        db.rollback()
    else:
        db.commit()

    db.close()

    # archive new runs
    for run in runs:
        archive = archives[run.server_name]
        year, month = run.date.split('-')[0:2]
        destdir = '%s/%s/%s' % (archive, year, month)
        destination = '%s/%s' % (destdir, run.run_id)
        print 'archive: %s -> %s' % (run.subdir, destdir)
        if not options.dry_run:
            if not exists(destdir):
                makedirs(destdir)
            rename(run.subdir, destination)


if __name__ == '__main__':
    main()
