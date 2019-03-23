#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import os
import datetime, time
import re
import logging
import sys
import argparse
import codecs
import argparse
import json
import yaml
import gzip
from functools import wraps
import ipdb

COMMON_PATTERN = '{0} {1}  - {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}'.format(
    r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    r'(?P<remote_user>(-|(\d+|\w+)*))',
    r'(?P<timestamp>\[\d{2}\/\w{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4}\])',
    r'(?P<request>\"(((GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) (?P<url>.+) HTTP\/1.(\d))|\d+)\")',
    r'(?P<status>\d{3})',
    r'(?P<bytes>\d+)',
    r'(?P<http_referer>\"((http|https):.+?|-)\")',
    r'(?P<user_agent>\".+?\")',
    r'(?P<forwarded_for>\"(.+?|-)\")',
    r'(?P<request_id>\"(-|.)+?\")',
    r'(?P<rb_user>\"-|.+?\")',
    r'(?P<request_time>(\d+|\.)*)'
)
LOGGING_FORMAT = "'[%(asctime)s] %(levelname).1s %(message)s'"
LOGGING_DATE_FORMAT = "'%Y.%m.%d %H:%M:%S'"

config = {
    "REPORT_SIZE": 100,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": './logfile',
    'TS_PATH': './ts.timestamp'
}
ERRORS_NUMBER = 0.5

def memoize(func):
    """ Remember the results of the previous execution by function name """

    cache = {}
    @wraps(func)
    def cached_perfomance(*args, **kwargs):
        key = func.__name__
        if key not in cache:
            cache[key] = func(*args, **kwds)
        return cache[key]
    return cached_perfomance

def median(lst):
    """ Count median for the given list """

    n = len(lst)
    if n < 1:
        return None
    if n % 2 == 1:
        return sorted(lst)[n//2]
    else:
        return sum(sorted(lst)[n//2-1:n//2+1])/2.0

def open_logs_file(params, filename):
    """
    Open logs file depending on its format
    :param params: script attributes
    :param filename: name of the appropriate log file
    :return: None
    """

    try:
        full_file_name = os.path.join(params['LOG_DIR'], filename)
        format_type = filename.split('.')[-1]
        if format_type == 'gz':
            with gzip.open(full_file_name) as f:
                return f
        else:
            with open(full_file_name) as f:
                return f
    except IOError:
        msg = 'There is no such file'
        raise AttributeError(msg)

def read_logs(filestream):
    """ Read logs data from the stream """

    requests_number = 0
    common_request_time = 0
    times = {}
    requests_data = []

    parse_errors_counter = 0
    logging.info('START: READING LOGS')
    for line in filestream:
        try:
            requests_number += 1
            data = re.search(COMMON_PATTERN, line)
            datadict = data.groupdict()

            url = datadict.get('url')
            request_time = datadict.get('request_time')

            params = {
                'url': url
            }
            requests_data.append(params)

            if times.get(url):
                times[url].append(float(request_time))
            else:
                times[url] = [float(request_time)]

            common_request_time += float(request_time)
        except Exception as e:
            parse_errors_counter += 1
            if float(parse_errors_counter) / float(requests_number) > ERRORS_NUMBER:
                requests_number = 0
                msg = 'Invalid log format'
                raise  AttributeError('Invalid log format')

    logging.info('STOP: READING LOGS')
    return {
        'requests_number': requests_number,
        'common_request_time': common_request_time,
        'times': times,
        'requests_data': requests_data
    }

def make_report_data(log_result):
    """ Prepare logs data for the report format """

    statistics = {}
    requests_data = log_result.get('requests_data')
    common_request_time = log_result.get('common_request_time')
    times = log_result.get('times')
    requests_number = log_result.get('requests_number')

    logging.info('START: PREPARING REPORT DATA')
    for item in requests_data:
        url = item.get('url')
        url_request_times = times.get(url)
        if statistics.get(url):
            statistics[url]['count'] += 1
            count_perc = (float(statistics[url]['count']) / requests_number) * 100
            statistics[url]['count_perc'] = count_perc
        else:
            times_sum = sum(url_request_times)
            statistics[str(url)] = {
                'count': 1,
                'count_perc': (1.0 / requests_number) * 100,
                'time_sum': times_sum,
                'time_perc': (times_sum / common_request_time) * 100,
                'time_avg': times_sum / len(url_request_times),
                'time_max': max(url_request_times),
                'time_med': median(url_request_times)
            }
    logging.info('STOP: PREPARING REPORT DATA')
    return statistics

def report_data_array(params, statistics):
    """
    Make a list from dictionary.
    :param params: script command line arguments
    :return: list of report values based on some conditions
    """

    try:
        data = []
        report_size = int(params['REPORT_SIZE'])

        for key, value in statistics.iteritems():
            data.append(dict({ 'url': key}, **value))
        return sorted(data, key=lambda item: item.get('time_sum'), reverse=True)[:report_size]
    except ValueError:
        logging.error('report_data_array: Value {} cannot be coerced to int'.format(params['REPORT_SIZE']))
        return []
    except KeyError:
        logging.error('No such key')
        return []

def read_config_file(filename):
    """
    :param file_name: Config's name file
    :return: dictionary with configuration information
    """

    try:
        format_type = filename.split('.')[-1]
        if format_type == 'json':
            return json.load(open(filename))
        elif format_type == 'yaml' or format_type == 'yml':
            return yaml.load(open(filename))
        else:
            return None
    except IOError:
        logging.error('There is no such config file: {}'.format(filename))
        return None

def set_logging_configuration(params):
    """
    Setting up logging data.
    :param params: script attributes
    :return: None
    """

    logfile = params.get('LOG_FILE')
    stream_value = None if logfile else sys.stdout
    logging.basicConfig(
        stream=stream_value, format=LOGGING_FORMAT,
        datefmt=LOGGING_DATE_FORMAT, filename=logfile, level=logging.INFO
    )

def get_external_config(params):
    """
    Parse config value and get config filename.
    :param params: script command line arguments
    :return: dict with external arguments / None
    """

    return read_config_file(params.config) if params.config else None

def get_common_params(external_config):
    """
    Merge external and default script configurations;
    :param local_config: external script configuration
    :return: dict
    """

    return dict(config, **external_config) if external_config else config

def get_last_log(params):
    """
    Get last actual log for the
    :param params: script attributes
    :return: name of the log / None
    """

    try:
        log_files = os.listdir(params['LOG_DIR'])
        pattern = re.compile('nginx-access-ui.log-{}'.format(get_log_date()))
        matched_files = filter(pattern.match, log_files)
        return matched_files[0]
    except OSError:
        logging.error('There is no such directory - {}'.format(params['LOG_DIR']))
        return False
    except KeyError:
        logging.error('Key does not present')
        return False
    except IndexError:
        logging.error('There is not files with such timestamp')
        return False

@memoize
def get_last_log_date():
    """
    Return last available log's date
    """

    files = os.listdir(os.path.join(params['LOG_DIR']))
    file_pattern = re.compile(r'nginx-access-ui.log-\d{6,8}')
    date_pattern = re.compile(r'\d{6,8}')
    last_log = sorted(filter(file_pattern.search, files), reverse=True)[0]
    if last_log:
        date_match = date_pattern.search(last_log)
        date_value = date_match.group(0)
        return datetime.datetime.strptime(date, '%Y%m%d').date()
    else:
        return datetime.datetime.now()

def get_log_date():
    """
    Return today's date in appropriate for logs format
    :return: crrent date's representation
    """

    return get_last_log_date().strftime('%Y%m%d')

def get_report_date():
    """
    Return today's date in appropriate for report format
    """

    return get_last_log_date().strftime('%Y.%m.%d')

def get_replaced_default_template(report_data):
    """
    Open default template and replace $table_json with report_data
    :param report_data: list of necessary objects for report
    :return: Content for the new page
    """

    try:
        f = codecs.open("./report.html", 'r')
        content = f.read()
        new_content = content.replace('$table_json', str(report_data))
        return new_content
    except IOError:
        logging.error('File report.html does not exist')

def resolve_report_name():
    """
    Form report name.
    :return: anme of report file
    """

    report_file_name = 'report-{}.html'.format(get_report_date())
    return os.path.join(params['REPORT_DIR'], report_file_name)

def write_report_data(params, report_data, report_path):
    """
    Write report data into file with appropriate parameters
    :param params: script attributes
    :param report_data: list of necessary objects for report
    :param report_path: path to the report file
    :return: None
    """

    try:
        report_page = get_replaced_default_template(report_data)
        new_report = open(report_path, 'w')
        new_report.write(report_page)
        new_report.close()
        logging.info(
            'Today\'s report was successfully generated. \
            You can find it here: {}'.format(report_path)
        )
    except IOError:
        logging.error('There is not such directory - {}'.format(params['REPORT_DIR']))

def parse_args():
    """
    Receive external and internal script parameters, merged together;
    :return: dict with attributes
    """

    parser = argparse.ArgumentParser(description='Get config file')
    parser.add_argument('--config', type=str, help='Name of the config file')
    params = parser.parse_args()
    external_config = get_external_config(params)
    return get_common_params(external_config)

def validate_config(params):
    """
    Validates whether or not report has already been generated
    :param params: script attributes
    :return: True / False
    """

    try:
        jquery_plugin_name = 'jquery.tablesorter.min.js'
        for item in ['REPORT_SIZE', 'REPORT_DIR', 'LOG_DIR']:
            if item not in params:
                logging.error('Key {} is not present'.format(item))
                return False
        js_path = os.path.join(params['REPORT_DIR'], jquery_plugin_name)
        if not os.path.exists(js_path):
            logging.error('{} does not present in {} directory'.format(jquery_plugin_name, params.get('REPORT_DIR')))
            return False
        if not os.path.isdir(params['REPORT_DIR']) or not os.path.isdir(params['LOG_DIR']):
            logging.error(
                'Something wrong with paths to the reports or logs'
            )
            return False
        return True
    except IOError as e:
        return False

def validate_report_generation(params):
    """
    Validate whether or not the report for the current
    timestamp was generated
    :param params: script attributes
    :return: True / False
    """

    report_files = os.listdir(params['REPORT_DIR'])
    pattern = re.compile('report-{}.html'.format(get_report_date()))
    matched_files = filter(pattern.match, report_files)
    return len(matched_files) == 0

def write_ts_file(params):
    """
    Write to the ts file current timestamp
    :param params: script attributes
    :return: None
    """

    try:
        t = datetime.datetime.now()
        time_value = time.mktime(t.timetuple())
        with open(params["TS_PATH"], 'w') as f:
            f.write(str(time_value))
            os.utime(params["TS_PATH"], (time_value, time_value))
    except KeyError:
        logging.error('There is not TS_PATH attribute')

def main():
    try:
        params = parse_args()
        set_logging_configuration(params)
        if not validate_config(params):
            raise AttributeError('Default configuration is invalid')

        report_name = resolve_report_name()

        if report_name:
            logging.info('The report for today is already present')
            write_ts_file(params)
            return

        last_log_name = get_last_log(params)
        if not last_log_name:
            logging.info('There is no log with today\'s timestamp')
            return

        file_data = open_logs_file(params, last_log_name)
        logs_result = read_logs(file_data)
        report_statistics = make_report_data(logs_result)
        report_data = report_data_array(params, report_statistics)
        write_report_data(params, report_data, report_name)
        write_ts_file(params)
    except KeyboardInterrupt:
        logging.exception('Keyboard interruption was called')
    except AttributeError as e:
        logging.exception(e.args[0])
    except  BrokenPipeError as e:
        logging.exception(e.args[0])

if __name__ == "__main__":
    main()
