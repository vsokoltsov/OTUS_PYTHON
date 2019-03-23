import sys
import os
import unittest
from contextlib import contextmanager
from mock import patch, mock_open
from log_analyzer import (
    read_config_file, validate_config, get_common_params, open_logs_file,
    read_logs, make_report_data, report_data_array
)

class LogAnalyzerTest(unittest.TestCase):
    """ Test cases for the log analyzer """

    def test_read_json_config(self):
        """ Test success reading of the json config """

        config = read_config_file('config.json')
        self.assertIsNotNone(config)

    def test_read_yaml_file(self):
        """ Test success reading of the yaml config """

        config = read_config_file('config.yaml')
        self.assertIsNotNone(config)

    def test_read_yml_file(self):
        """ Test success reading of the yml config """

        config = read_config_file('config.yml')
        self.assertIsNotNone(config)

    def test_common_params_receiving(self):
        """ Tests merging of internal and external parameters if config option is given """

        external_config = read_config_file('config.json')
        config = get_common_params(external_config)
        self.assertTrue('log_dir' in config)
        self.assertTrue('REPORT_DIR' in config)

    def test_receiving_internal_config_only(self):
        """ Test receiving only internal config if external was not provided """

        config = get_common_params(None)
        self.assertFalse('log_dir' in config)
        self.assertTrue('REPORT_DIR' in config)

    def test_failed_report_existence_validation(self):
        """ Tests failed report validation if js library is abscent """

        external_config = read_config_file('config.json')
        config = get_common_params(external_config)
        self.assertFalse(validate_config(config))

    def test_success_report_existance_validation(self):
        """ Tests success report validation if js library is present """

        external_config = read_config_file('config.json')
        config = get_common_params(external_config)
        if not os.path.exists(config.get('REPORT_DIR')):
            os.makedirs(config.get('REPORT_DIR'))

        file_path = '{}/jquery.tablesorter.min.js'.format(config.get('REPORT_DIR'))
        f = open(file_path, 'a')
        f.close()
        self.assertTrue(validate_config(config))
        os.remove(file_path)

    def test_opening_plain_log_file(self):
        """ Test of opening the plain log file """

        config = get_common_params(None)
        config['LOG_DIR'] = './tests'
        file_name = 'test_log'
        full_path = '{}/{}'.format(config['LOG_DIR'], file_name)
        with patch("__builtin__.open", mock_open(read_data="data")) as mock_file:
            open_logs_file(config, file_name)
            assert open(full_path).read() == "data"
            mock_file.assert_called_with(full_path)

    @patch('gzip.open', create=True)
    def test_opening_gzip_file_log(self, gzip_mock):
        """ Test of opening the zipped log file """

        config = get_common_params(None)
        config['LOG_DIR'] = './tests'
        file_name = 'test_log.gz'
        full_path = '{}/{}'.format(config['LOG_DIR'], file_name)
        open_logs_file(config, file_name)
        self.assertTrue(gzip_mock.called)

    def test_failed_opening_of_log_file(self):
        """ Test raising of the exception if the file does not exist """

        config = get_common_params(None)
        config['LOG_DIR'] = './tests'
        file_name = 'test'
        full_path = '{}/{}'.format(config['LOG_DIR'], file_name)
        with self.assertRaises(AttributeError) as context:
            open_logs_file(config, file_name)

    def test_success_log_reading(self):
        """ Test case of success logs reading """

        expected_request_number = 14
        config = get_common_params(None)
        config['LOG_DIR'] = './tests'
        file_name = 'test_log'
        full_path = '{}/{}'.format(config['LOG_DIR'], file_name)
        with open(full_path, 'r') as f:
            results = read_logs(f)
            self.assertEqual(results.get('requests_number'), expected_request_number)

    def test_failed_log_reading(self):
        """ Test case of failed log reading """

        config = get_common_params(None)
        config['LOG_DIR'] = './tests'
        file_name = 'failed_log'
        full_path = '{}/{}'.format(config['LOG_DIR'], file_name)
        with self.assertRaises(AttributeError) as context:
            with open(full_path) as f:
                read_logs(f)

    def test_making_report_data(self):
        """ Test making report data base on request data """

        log_result = {}
        log_result['statistics'] = {}
        log_result['requests_number'] = 4
        log_result['times'] = {
            '/api/v1/aaa': [0.01, 0.002],
            '/api/v2/ccc': [0.005, 115.21]
        }
        log_result['requests_data'] = [
            { 'url': '/api/v1/aaa' },
            { 'url': '/api/v2/ccc' },
        ]
        log_result['common_request_time'] = sum([ sum(v) for k, v in log_result['times'].iteritems() ])

        results = make_report_data(log_result)
        self.assertIsNotNone(results)


    def test_report_result_by_url_containing(self):
        """ Test report by containing all the necessary urls """

        log_result = {}
        log_result['statistics'] = {}
        log_result['requests_number'] = 4
        log_result['times'] = {
            '/api/v1/aaa': [0.01, 0.002],
            '/api/v2/ccc': [0.005, 115.21]
        }
        log_result['requests_data'] = [
            { 'url': '/api/v1/aaa' },
            { 'url': '/api/v2/ccc' },
        ]
        log_result['common_request_time'] = sum([ sum(v) for k, v in log_result['times'].iteritems() ])
        results = make_report_data(log_result)

        self.assertTrue('/api/v1/aaa' in results)
        self.assertTrue('/api/v2/ccc' in results)

    def test_report_url_count(self):
        """ Test correct value of calculated information for every url """

        log_result = {}
        log_result['statistics'] = {}
        log_result['requests_number'] = 4
        log_result['times'] = {
            '/api/v1/aaa': [0.01, 0.002],
            '/api/v2/ccc': [0.005, 115.21]
        }
        log_result['requests_data'] = [
            { 'url': '/api/v1/aaa' },
            { 'url': '/api/v2/ccc' },
        ]
        log_result['common_request_time'] = sum([ sum(v) for k, v in log_result['times'].iteritems() ])

        results = make_report_data(log_result)

        self.assertTrue(results['/api/v1/aaa']['count'], 1)
        self.assertTrue(results['/api/v2/ccc']['count'], 1)

    def test_success_report_data_construction(self):
        """ Test correct forming of the final scope of logs """

        config = get_common_params(None)
        log_result = {}
        log_result['statistics'] = {}
        log_result['requests_number'] = 4
        log_result['times'] = {
            '/api/v1/aaa': [0.01, 0.002],
            '/api/v2/ccc': [0.005, 115.21]
        }
        log_result['requests_data'] = [
            { 'url': '/api/v1/aaa' },
            { 'url': '/api/v2/ccc' },
        ]
        log_result['common_request_time'] = sum([ sum(v) for k, v in log_result['times'].iteritems() ])

        results = make_report_data(log_result)
        data = report_data_array(config, results)
        self.assertEqual(len(data), 2)

    def test_failed_report_data_construction(self):
        """ Test failed creation of the resulting list """

        config = get_common_params(None)
        config['REPORT_SIZE'] = 'aaa'

        log_result = {}
        log_result['statistics'] = {}
        log_result['requests_number'] = 4
        log_result['times'] = {
            '/api/v1/aaa': [0.01, 0.002],
            '/api/v2/ccc': [0.005, 115.21]
        }
        log_result['requests_data'] = [
            { 'url': '/api/v1/aaa' },
            { 'url': '/api/v2/ccc' },
        ]
        log_result['common_request_time'] = sum([ sum(v) for k, v in log_result['times'].iteritems() ])

        results = make_report_data(log_result)
        data = report_data_array(config, results)
        self.assertEqual(len(data), 0)
        config['REPORT_SIZE'] = 100

if __name__ == '__main__':
    unittest.main()
