#!/usr/bin/env python
#
# Author: Bruno E O Meneguele <bruno.meneguele@smartgreen.net>
# Company: Smartgreen S.A.

import os
import re
import socket
import tarfile
import tempfile
import shutil
import argparse


class LogParser(object):
    """Class responsible to handle the logs and get specific points of it based on data and time information passed by
    arguments.
    """

    def __init__(self, date_range, time_range, log_dir, log_prefix, output_name):
        """Instantiates the log parser and parser all log paths requested. It also transforms date format from
        '2015-02-01,2016-01-01' to a list of integers [20150201, 20160101] which it's easier and faster to compare.
        """

        if not date_range:
            self.date_range = None
        else:
            self.date_range = [int(''.join(date.split('-', 2))) for date in date_range.split(',')]

        if not time_range:
            self.time_range = None
        else:
            self.time_range = [int(''.join(time.split(':', 3))) for time in time_range.split(',')]

        self.log_dir = log_dir
        self.log_files = log_prefix.split(',')

        if output_name == '':
            output_name = ''.join([self._sgcon_get_hostname(), '-logs.tar.gz'])

        self.output_name = output_name

        # Get all files with the same prefix (lpre) in case * is passed as part of any log_prefix argument
        aux_files = []

        for lfile in self.log_files:
            if lfile.count('*'):
                lpre, _ = lfile.split('*', 1)

                for files in os.listdir(self.log_dir):
                    matches = re.match(r'({}.*)'.format(lpre), files)

                    if not matches:
                        continue

                    aux_files.extend(matches.groups())
                    aux_files = sorted(aux_files, reverse=True)

        # Join all requested files to the log_path. i.e. /var/log/sgcon +
        # suiteCore = /var/log/sgcon/suiteCore
        self.log_files = aux_files
        self.log_paths = [os.path.join(self.log_dir, lfile) for lfile in self.log_files]
        self.bkp_files_path = tempfile.mkdtemp()

        self.print_infos()

    @staticmethod
    def _sgcon_get_hostname():
        return socket.gethostname()

    def print_infos(self):
        if self.date_range:
            print "INFO: start date is {0}, end date is {1}".format(*self.date_range)

        if self.time_range:
            print "INFO: start time is {0}, end time is {1}".format(*self.time_range)

        print "INFO: log files:"

        for log in self.log_files:
            print "    {}".format(log)

        print "INFO: output file: {0}".format(self.output_name)

    # Log line example:
    def search_logs(self):
        """ Get all log lines among date and time range following the format:

        "2016-01-25 11:13:21,330 PowerMonitor INFO MainThread Service stopped."
        """

        # Regular expression to match both date and time information at once, naming its presence group as <date> and
        # <time>. Date and time must have the pre defined formats used here.
        re_date_time = re.compile(r'(?P<date>\d{4}-\d{2}-\d{2})\s*(?P<time>\d{2}:\d{2}:\d{2})')
        bkp_files = set()

        # Check for every log file present in the log_dir
        for log_path in self.log_paths:
            m_lines = []

            with open(log_path, 'r') as log:
                flines = log.readlines()

                for line in flines:
                    m_date_time = re_date_time.match(line)
                    m_date = m_date_time.group('date') if self.date_range and m_date_time else None
                    m_time = m_date_time.group('time') if self.time_range and m_date_time else None

                    # Rules to handle user specific date and/or time ranges.
                    if m_date and m_time:
                        m_date_value = int(''.join(m_date.split('-', 2)))
                        m_time_value = int(''.join(m_time.split(':', 3)))

                        if self.date_range[0] <= m_date_value <= self.date_range[1] and \
                                self.time_range[0] <= m_time_value <= self.time_range[1]:
                            m_lines.append(line)
                        elif m_date_value > self.date_range[1] or m_time_value > self.time_range[1]:
                            break
                    elif not m_date and m_time:
                        m_time_value = int(''.join(m_time.split(':', 3)))

                        if self.time_range[0] <= m_time_value <= self.time_range[1]:
                            m_lines.append(line)
                    elif m_date and not m_time:
                        m_date_value = int(''.join(m_date.split('-', 2)))

                        if self.date_range[0] <= m_date_value <= self.date_range[1]:
                            m_lines.append(line)
                        elif m_date_value > self.date_range[1]:
                            break

            if m_lines:
                tmp = '{}.log'.format(os.path.join(self.bkp_files_path, os.path.basename(log_path).split('.')[0]))
                bkp_files.add(tmp)

                with open(tmp, 'a+') as bkp_file:
                    map(bkp_file.write, m_lines)

        return bkp_files

    def compress_logs(self, logs):
        with tarfile.open(self.output_name, 'w:gz') as tar_file:
            for log in logs:
                os.chdir(os.path.dirname(log))
                tar_file.add(os.path.basename(log))

        shutil.rmtree(self.bkp_files_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get any log based in the Python 'logging' module from a date and time\
                                     range")

    parser.add_argument('-d',
                        action='store',
                        dest='date_range',
                        type=str,
                        default='',
                        help="Set the date range from the beginning to the end. Example: 01-01-2010,31-12-2015"
                        )

    parser.add_argument('-t',
                        action='store',
                        dest='time_range',
                        type=str,
                        default='',
                        help="Set the time range from the beginning to the end. Example: 00:00:00,23:59:59"
                        )

    parser.add_argument('-p',
                        action='store',
                        dest='log_prefix',
                        type=str,
                        default='*',
                        help="Get logs based on its name prefix. Example: powerMonitor*,suiteCore,network"
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

    if not args.time_range and not args.date_range:
        parser.error("you must set at least a date or time range.")
        exit(1)

    log_parser = LogParser(
        args.date_range,
        args.time_range,
        args.log_dir,
        args.log_prefix,
        args.output_name)
    log_parser.compress_logs(log_parser.search_logs())
