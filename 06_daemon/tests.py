import unittest
import ipdb
from wsgi import get_ip_info, get_weather_info

class WeatherByIpInfo(unittest.TestCase):
    """ Unittests for the actions in wsgi daemon server """

    def test_receiving_of_ip_without_params(self):
        """ Returns ip information for current user ip """

        result = get_ip_info()
        self.assertTrue('error' not in result)

    def test_receiving_of_ip_wit_params(self):
        """ Returns ip information for current user ip """

        result = get_ip_info(ip_value='176.14.221.123')
        self.assertTrue(result.get('city') == 'Moscow')

    def test_weather_info_without_coords(self):
        """ Return None if user coordinates are wrong """

        result = get_weather_info(coords=('a', 'b'))
        self.assertTrue(result['cod'] == '400')

    def test_weather_info_with_coords(self):
        """ Return None if user coordinates are wrong """

        result = get_ip_info(ip_value='176.14.221.123')
        lat, long = result.get('loc').split(',')
        weather = get_weather_info(coords=(float(lat), float(long)))
        self.assertTrue(weather['name'] == 'Moscow' )
