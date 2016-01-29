import os
import re
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
        It also transforms date format from '2015-02-01,2016-01-01' to a list of
        integers [20150201, 20160101] which it's easier and faster to compare.
        """

        self.date_range = [int(''.join(date.split('-', 2)))
                           for date in date_range.split(',')]
        self.time_range = time_range.split(',')
        self.log_dir = log_dir
        self.log_files = log_prefix.split(',')

        print "INFO: start date is {0}, end date is {1}".format(
                *self.date_range)

        if output_name == '':
            output_name = ''.join([self._sgcon_get_hostname(), '-logs.tar.gz'])

        self.output_name = output_name

        # Get all files with the same prefix (lpre) in case * is passed as part
        # of any log_prefix argument
        for lfile in self.log_files:
            if lfile.count('*'):
                lpre, _ = lfile.split('*', 1)
                self.log_files.remove(lfile)

                for f in os.listdir(self.log_dir):
                    matches = re.search(r'({}.*)'.format(lpre), f)

                    if not matches:
                        continue

                    self.log_files.extend(matches.groups())
                    self.log_files = sorted(self.log_files, reverse=True)

        # Join all requested files to the log_path. i.e. /var/log/sgcon +
        # suiteCore = /var/log/sgcon/suiteCore
        self.log_paths = [os.path.join(self.log_dir, lfile)
                          for lfile in self.log_files]

        print 'Log files:'
        print self.log_paths

    @staticmethod
    def _sgcon_get_hostname(self):
        return socket.gethostname()

    # Log line example:
    def get_logs(self):
        """ Get all log lines among date and time range following the format:

        "2016-01-25 11:13:21,330 PowerMonitor INFO MainThread Service stopped."
        """

        re_date = re.compile(r'(\d{4}-\d{2}-\d{2})')

        for log_path in self.log_paths:
            m_lines = []

            with open(os.path.realpath(log_path)) as log:
                for line in log.readlines():
                    m = re_date.match(line)

                    if m:
                        m_value = int(''.join(m.group(0).split('-', 2)))

                        if self.date_range[0] <= m_value <= self.date_range[1]:
                            m_lines.append(line)

                bkp_file_path = os.path.dirname(os.path.realpath(
                        self.output_name))

            if m_lines:
                with open('{0}/{1}'.format(bkp_file_path, os.path.basename(
                        log_path)), 'w+') as bkp_file:
                    map(bkp_file.write, m_lines)

    def compress_logs(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get any log based in the\
                                     Python 'logging' module from a date and time\
                                     range")

    parser.add_argument('-d',
                        action='store',
                        dest='date_range',
                        type=str,
                        default='*',
                        help="Set the date range from the begining to the end.\
                        Example: 01-01-2010,31-12-2015"
                        )

    parser.add_argument('-t',
                        action='store',
                        dest='time_range',
                        type=str,
                        default='*',
                        help="Set the time range from the begining to the end.\
                        Example: 00:00:00,23:59:59"
                        )

    parser.add_argument('-p',
                        action='store',
                        dest='log_prefix',
                        type=str,
                        default='*',
                        help="Get logs based on its name prefix.\
                        Example: powerMonitor*,suiteCore,network"
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
    log_parser.get_logs()
