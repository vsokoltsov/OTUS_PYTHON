import redis
import time
import logging

class RedisStore(object):
    """ Redis store class """

    HOST = 'localhost'
    PORT = 6379
    DB = 0
    ATTEMPTS_COUNT = 3
    SLEEP_TIME = 15
    TIMEOUT = 0.5

    def __init__(self, **kwargs):
        """ Base contstructor; Connect to redis """

        self.cache = {}
        sleep_time = kwargs.get('sleep_time', self.SLEEP_TIME)
        params = {
            'host': kwargs.get('host', self.HOST),
            'port': kwargs.get('port', self.PORT),
            'db': kwargs.get('db', self.DB),
            'socket_timeout': kwargs.get('socket_timeout', self.TIMEOUT)
        }
        attempts = 0
        while attempts < self.ATTEMPTS_COUNT:
            try:
                self.redis = redis.Redis(**params)
                self.redis.ping()
                break
            except redis.exceptions.ConnectionError, e:
                logging.info('Redis connection failed. Sleep for {} seconds'.format(sleep_time))
                time.sleep(sleep_time)
            finally:
                attempts += 1

        if attempts == self.ATTEMPTS_COUNT:
            self.redis = None
            logging.info(
                'Not able to connect via host {} port {}. Switching to local hash'.format(self.HOST, self.PORT)
            )

    def get(self, key):
        """ Get value from the redis store """

        try:
            return self.redis.get(key)
        except AttributeError:
            raise ValueError('Store is not available')

    def cache_get(self, key):
        """ Get value from the local cache """

        return self.cache.get(key)

    def cache_set(self, key, val):
        """ Set value with expiration date """

        self.cache[key] = val

    def set(self, key, val, exp=None):
        """ Set value to the redis and cache store """

        try:
            if self.redis:
                self.redis.set(key, val)
            if exp:
                self.redis.expire(key, exp)
        except AttributeError:
            raise ValueError('Store is not available')
