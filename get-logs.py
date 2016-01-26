import os
import sys
import re
import mmap
import socket
import tarfile
import argparse

class LogParser(object):
    """Class responsible to handle the logs and get specific points of it based
    on data and time information passed by arguments.
    """

    def __init__(self, date_range, time_range, log_dir, log_prefix,
                 output_name):
        """Instantiates the log parser and parser all log paths requested.
        """

        self.date_range = date_range.split(',')
        self.time_range = time_range.split(',')
        self.log_dir = log_dir
        self.log_files = log_prefix.split(',')

        if output_name == '':
            output_name = ''.join([self._sgcon_get_hostname(), '-logs.tar.gz'])

        self.output_name = output_name

        # Get all files with the same prefix (lpre) in case * is passed as part
        # of any log_prefix argument
        for lfile in self.log_files:
            if lfile.count('*'):
                lpre, _ = lfile.split('*', 1)
                print 'lpre: ', lpre
                self.log_files.remove(lfile)

                for f in os.listdir(self.log_dir):
                    matches = re.search(r'({}.*)'.format(lpre), f)

                    if not matches:
                        continue

                    self.log_files.extend(matches.groups())


        # Join all requested files to the log_path. i.e. /var/log/sgcon +
        # suiteCore = /var/log/sgcon/suiteCore
        self.log_paths = [os.path.join(self.log_dir, lfile)
                         for lfile in self.log_files]

        print 'Log files:'
        print self.log_paths
        print 'Output file: ', self.output_name
        self.get_logs()

    def _sgcon_get_hostname(self):
        return socket.gethostname()

    # Log line example:
    # 2016-01-25 11:13:21,330 PowerMonitor INFO MainThread Service stopped.
    def get_logs(self):
        """ Get all log lines among date and time range.
        """

        start_lnum = end_lnum = 0
        pattern = [r'({}.*)'.format(date) for date in self.date_range]

        for log_file in self.log_paths:
            with open(os.path.realpath(log_file), 'r') as log:
                start_lnum, end_lnum = self._get_lnums(log, pattern)

                if start_lnum != 0 and end_lnum != 0:
                    print start_lnum, end_lnum
                    break
                else:
                    # TODO: it's possible the end_lnum isn't in the same file
                    if start_lnum == 0:
                        print >> sys.stderr, "ERROR: start_lnum was not found."
                    elif end_lnum == 0:
                        print >> sys.stderr, "ERROR: end_lnum was not found."

    def _get_lnums(self, f, pattern):
        """ Find the line numbers of the start line and the end line to the
        requested date and time range.
        """

        start_lnum = end_lnum = 0

        # First try to find the start line number, then search for the end line.
        for lnum, line in enumerate(f.readlines(), 1):
            if start_lnum == end_lnum == 0:
                if re.search(pattern[0], line):
                    start_lnum = lnum

            if start_lnum != 0 and end_lnum == 0:
                if re.search(pattern[1], line):
                    end_lnum = lnum

        return (start_lnum, end_lnum)

    def compress_logs(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get all SG Concentrador logs")

    parser.add_argument('-d',
                        action='store',
                        dest='date_range',
                        type=str,
                        default='*',
                        help="Set the date range from the begining to the end\
                        separated by commas (,). Example: 01-01-2010,31-12-2015"
                        )

    parser.add_argument('-t',
                        action='store',
                        dest='time_range',
                        type=str,
                        default='*',
                        help="Set the time range from the begining to the end\
                        separated by commas (,). Example: 00:00:00,23:59:59"
                        )

    parser.add_argument('-p',
                        action='store',
                        dest='log_prefix',
                        type=str,
                        default='*',
                        help="Get logs based on its name prefix separated by\
                        commas (,). Example: powerMonitor,suiteCore,network"
                        )

    parser.add_argument('--log-dir',
                        action='store',
                        dest='log_dir',
                        type=str,
                        default='/var/log/sgcon/',
                        help="Absolute path to the log directory"
                        )

    parser.add_argument('-o',
                        action='store',
                        dest='output_name',
                        type=str,
                        default='',
                        help="Output TAR filename."
                        )

    args = parser.parse_args()

    log_parser = LogParser(
        args.date_range,
        args.time_range,
        args.log_dir,
        args.log_prefix,
        args.output_name)
