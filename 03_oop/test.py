# -*- coding: utf-8 -*-

import unittest

import ipdb
import datetime
import time
import redis
from store import RedisStore
from functools import wraps
import mock

from api import (
    ClientsInterestsRequest, OnlineScoreRequest, CharField, ArgumentsField, Field,
    EmailField, PhoneField, DateField, BirthDayField, GenderField, ClientIDsField
)

class MockClass(object):
    """ Class for descriptors testing """
    errors = {}

def cases(cas):
    """ Run tests through all the passed cases """

    def actual_func(func):
        def performed_with_cases(*args, **kwargs):
            for item in cas:
                default_doc = func.__doc__
                func.__doc__ = func.__doc__.format(item)
                kwargs['request'] = item
                func(*args, **kwargs)
                func.__doc__ = default_doc
        return performed_with_cases
    return actual_func

class CharFieldTests(unittest.TestCase):
    """ Tests for CharField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """

        MockClass.test = CharField(name='test')
        mock_class = MockClass()
        val = 'test'
        MockClass.__dict__['test'].__set__(mock_class, val)
        self.assertTrue(
            mock_class.test, val
        )

class ArgumentsFieldTests(unittest.TestCase):
    """ Tests for ArgumentsField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """

        MockClass.arguments = ArgumentsField(name='arguments')
        mock_class = MockClass()
        val = { 'a': 'b' }
        MockClass.__dict__['arguments'].__set__(mock_class, val)
        self.assertTrue(mock_class, val)

    def test_failed_assertion(self):
        """ Test failed assertion """

        MockClass.arguments = ArgumentsField(name='arguments')
        mock_class = MockClass()
        val = '1'
        with self.assertRaises(ValueError):
            MockClass.__dict__['arguments'].__set__(mock_class, val)

class EmailFieldTests(unittest.TestCase):
    """ Tests for EmailField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """

        MockClass.email = EmailField(name='email')
        mock_class = MockClass()
        val = 'example@mail.com'
        MockClass.__dict__['email'].__set__(mock_class, val)
        self.assertTrue(mock_class.email, val)

    def test_failed_assertion(self):
        """ Test failed assertion """

        MockClass.email = EmailField(name='email')
        mock_class = MockClass()
        val = 'examplemail.com'
        with self.assertRaises(ValueError):
            MockClass.__dict__['email'].__set__(mock_class, val)


class PhoneFieldTests(unittest.TestCase):
    """ Tests for PhoneField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """

        MockClass.phone = PhoneField(name='phone')
        mock_class = MockClass()
        val = '79157373038'
        MockClass.__dict__['phone'].__set__(mock_class, val)
        self.assertTrue(mock_class.phone, val)

    def test_failed_assertion(self):
        """ Test failed assertion """

        MockClass.phone = PhoneField(name='phone')
        mock_class = MockClass()
        val = '+12179157373038'
        with self.assertRaises(ValueError):
            MockClass.__dict__['phone'].__set__(mock_class, val)

class DateFieldTests(unittest.TestCase):
    """ Tests for DateField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """

        MockClass.date = DateField(name='date')
        mock_class = MockClass()
        val = '02.03.1993'
        MockClass.__dict__['date'].__set__(mock_class, val)
        self.assertTrue(mock_class.date, val)

    def test_failed_assertion(self):
        """ Test failed assertion """

        MockClass.date = DateField(name='date')
        mock_class = MockClass()
        val = '02031993'
        with self.assertRaises(ValueError):
            MockClass.__dict__['date'].__set__(mock_class, val)


class BirthdayFieldTests(unittest.TestCase):
    """ Tests for BirthdayField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """


        MockClass.birthday = BirthDayField(name='birthday')
        mock_class = MockClass()
        val = '02.03.1993'
        MockClass.__dict__['birthday'].__set__(mock_class, val)
        self.assertTrue(
            mock_class.birthday, datetime.datetime.strptime(val, '%d.%m.%Y')
        )

    def test_failed_assertion(self):
        """ Test failed assertion """

        MockClass.birthday = BirthDayField(name='birthday')
        mock_class = MockClass()
        val = '02.03.1903'
        with self.assertRaises(ValueError):
            MockClass.__dict__['birthday'].__set__(mock_class, val)

class GenderFieldTests(unittest.TestCase):
    """ Tests for GenderField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """

        MockClass.gender = GenderField(name='gender')
        mock_class = MockClass()
        val = 1
        MockClass.__dict__['gender'].__set__(mock_class, val)
        self.assertTrue(mock_class.gender, 'MALE')

    def test_failed_assertion(self):
        """ Test failed assertion """

        MockClass.gender = GenderField(name='gender')
        mock_class = MockClass()
        val = 10
        field = GenderField()
        with self.assertRaises(ValueError):
            MockClass.__dict__['gender'].__set__(mock_class, val)

class ClientIDsFieldTests(unittest.TestCase):
    """ Tests for ClientIDsField descriptor """

    def test_success_assertion(self):
        """ Test success assertion """

        MockClass.clients = ClientIDsField(name='clients')
        mock_class = MockClass()
        val = [1, 2, 3]
        MockClass.__dict__['clients'].__set__(mock_class, val)
        self.assertTrue(mock_class.clients, val)

    def test_failed_assertion(self):
        """ Test failed assertion """

        MockClass.clients = ClientIDsField(name='client_ids')
        mock_class = MockClass()
        val = [{1,2,3}]
        with self.assertRaises(ValueError):
            MockClass.__dict__['clients'].__set__(mock_class, val)

class RedisStoreTestSuite(unittest.TestCase):
    """ Tests for RedisStore class """

    def test_success_initalization(self):
        """ Test success initialization of the store """

        store = RedisStore()
        self.assertIsNotNone(store)

    def test_failed_initialization(self):
        """ Test failed initialization of the store """

        store = RedisStore(host='test', sleep_time=0.1)
        self.assertIsNone(store.redis)

    def test_getting_value_to_redis(self):
        """ Test getting value from the redis """

        val = 'value'
        store = RedisStore()
        store.redis.set('test', val)

        self.assertEqual(store.get('test'), val)

    def test_setting_value(self):
        """ Test setting value to the redis """

        val = 'value'
        store = RedisStore()
        store.set('key', val)
        self.assertTrue(store.redis.get('key'), val)

    def test_getting_value_from_cache(self):
        """ Test getting value from the cache """

        val = 'value'
        key = 'key'
        store = RedisStore(host='test', sleep_time=0.1)
        store.cache_set(key, val)
        self.assertEqual(store.cache_get(key), val)

    def test_setting_value_with_expiration(self):
        """ Test expiration of the new key """

        val = 'value'
        key = 'key'
        store = RedisStore()
        store.set(key, val, 1)
        time.sleep(2)
        self.assertIsNone(store.get(key))

    def test_setting_value_redis_abscent(self):
        """ Test setting value if redis is abscent """

        val = 'value'
        key = 'key'
        store = RedisStore(host='test', sleep_time=0.1)
        with self.assertRaises(ValueError):
            store.set(key, val, 1)


class ClientsInterestsRequestTests(unittest.TestCase):
    """ Tests for the clients interesests requests through cases """

    def setUp(self):
        """ Setting up test dependencies """

        self.context = {}
        self.store = RedisStore()

    @cases([
        { "client_ids": [1,2,3,4], "date": "20.07.2017" },
        { "client_ids": [1,2,4], "date": "09.07.1993" },
        { "client_ids": [1], "date": "09.04.1983" }
    ])
    def test_success_response(self, request):
        """ Success response with case {} """

        client_interests = ClientsInterestsRequest(**request)
        response, code = client_interests.perform(self.context, self.store)
        self.assertEqual(code, 200)

    @cases([
        { "date": "20.07.2017" },
        { "client_ids": [1,2,4], "date": "09071993" }
    ])
    def test_failed_response(self, request):
        """ Test failed response with {} """

        with self.assertRaises(ValueError):
            ClientsInterestsRequest(**request)

class OnlineScoreRequestTests(unittest.TestCase):
    """ Tests for the online score requests through some cases """

    def setUp(self):
        """ Setting up test dependencies """

        self.context = {}
        self.store = RedisStore()

    @cases([
        { "phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
         "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1 },
        {
         "phone": "79157373038", "email": u"vs@gmail.com", "first_name": "V",
         "last_name": "S", "birthday": "09.07.1993", "gender": 1
         },
        {
         "phone": "79150010203", "email": u"teeest@otus.ru", "first_name": "wadawd",
         "last_name": "wdawdaw", "birthday": "01.01.1990", "gender": 1
         }
    ])
    def test_succcess_response(self, request):
        """ Success response with case {} """

        online_score = OnlineScoreRequest(**request)
        response, code = online_score.perform(self.context, self.store)
        self.assertEqual(code, 200)

    @cases([
        { "phone": "+79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
         "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1 },
        {
         "phone": "79157373038", "gender": 1
         },
        {
         "phone": "79150010203", "email": "twadawdotus.ru", "first_name": "wadawd",
         "last_name": "wdawdaw", "birthday": "01.01.1990", "gender": 1
         }
    ])
    def test_failed_response(self, request):
        """ Test failed response with {} """

        with self.assertRaises(ValueError):
            OnlineScoreRequest(**request)


if __name__ == "__main__":
    unittest.main()
