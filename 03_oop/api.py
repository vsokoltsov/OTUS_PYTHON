#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
from dateutil.relativedelta import relativedelta
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import inspect
import ipdb
import re
import scoring
from store import RedisStore

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

GENDER_IDS = [
    UNKNOWN, MALE, FEMALE
]

class Field(object):
    """ Base field class """

    def __init__(self, value=None, **kwargs):
        """ Default constructor """

        self.required = kwargs.get('required', False)
        self.nullable = kwargs.get('nullable', True)
        self.value = value
        self.name = kwargs.get('name', None)

    def __get__(self, obj, objtype):
        """ Default getter """

        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        """ Default setter """

        if not self.nullable and value is None:
            self._set_error('Should not be null')

        obj.__dict__[self.name] = value

    def _set_error(self, obj, error_text):
        """ Set error key to errors and raise exception """

        obj.errors[self.name] = error_text
        raise ValueError({ self.name: error_text })

class DescriptorsOwner(type):
    """ Metaclass for labeling the descriptors """

    def __new__(cls, name, bases, attrs):
        """ Find all descriptors and set their labels """

        for key, value in attrs.iteritems():
            if isinstance(value, Field):
                value.name = key
        return super(DescriptorsOwner, cls).__new__(cls, name, bases, attrs)

class InspectAttributesMixin(object):
    """ Class mixin for inspecting attributes """

    fields = []
    errors = {}

    def __init__(self):
        fields = [
            attr for attr in dir(self) if not callable(getattr(self, attr)) and
                not attr.startswith("__")
        ]
        fields.remove('fields')
        fields.remove('errors')
        self.fields = fields

class Request(InspectAttributesMixin):
    """ Base request class """
    __metaclass__ = DescriptorsOwner

    def __init__(self, data=None, **kwargs):
        """ Default constructor """

        super(Request, self).__init__()
        if data and isinstance(data, dict):
            self._set_attributes(data)
        else:
            self._set_attributes(kwargs)

    def _set_attributes(self, attrs):
        """ Set instance attributes """

        for key in self.fields:
            value = attrs.get(key)
            descriptor = self.__class__.__dict__.get(key)
            if value is None and descriptor.required:
                raise ValueError('Field %s is required' % key)
            setattr(self, key, value)

    @abc.abstractmethod
    def perform(self, context, store):
        """ Perform apporpriate query for particular class """
        pass

class CharField(Field):

    def __set__(self, obj, value):
        """ Setter for the char field; Cast all values to string """

        Field.__set__(self, obj, value)

        try:
            obj.__dict__[self.name] = str(value.encode('utf-8'))
        except UnicodeDecodeError, e:
            obj.__dict__[self.name] = str(value)
        except Exception, e:
            self._set_error(obj, 'Cannot be casted to string')


class ArgumentsField(Field):

    def __set__(self, obj, value):
        """ Setter for the dictionary field; Cast all values to dictionary """

        try:
            obj.__dict__[self.name] = dict(value)
        except (ValueError, TypeError), e:
            self._set_error(obj, 'Cannot be casted to dictionary')


class EmailField(CharField):
    def __set__(self, obj, value):
        """ Setter for the email field; Validate email field by regexp """

        Field.__set__(self, obj, value)
        if value and not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value):
            self._set_error(obj, 'Is not an email address')


class PhoneField(Field):
    def __set__(self, obj, value):
        """ Setter for the phone field; Validate email field by regexp """

        Field.__set__(self, obj, value)

        if value and not re.match(r'^(7)[0-9]{10}', value):
            self._set_error(obj, 'Invalid phone number')


class DateField(Field):
    def __set__(self, obj, value):
        """ Setter for the date field; Validate date regexp """


        Field.__set__(self, obj, value)
        if not re.match(r'^\d{2}.\d{2}.\d{4}$', value):
            self._set_error(obj, 'Invalid date format')


class BirthDayField(DateField):

    def __set__(self, obj, value):
        """ Setter for the birthday field; Validate by presence """

        try:
            date = datetime.datetime.strptime(value, '%d.%m.%Y')

            Field.__set__(self, obj, date)

            if value:
                now_date = datetime.datetime.now()
                years_diff = relativedelta(now_date, date).years
                if years_diff > 70:
                    self._set_error(obj, 'Birthday is more than 70 years ago')
        except:
            self._set_error(obj, 'Invalid date')


class GenderField(Field):
    def __set__(self, obj, value):
        """ Setter for the gender field; Validate by presence """

        Field.__set__(self, obj, value)

        if value and value not in GENDER_IDS:
            self._set_error(obj, 'Invalid gender value')

    def __get__(self, obj, objtype):
        """ Return string representation of the gender """

        gender = MALE

        if self.value == FEMALE:
            gender = FEMALE
        elif self.value == UNKNOWN:
            gender = UNKNOWN

        return gender


class ClientIDsField(Field):

    def __set__(self, obj, value):
        """ Setter for the gender field; Validate by presence """

        Field.__set__(self, obj, value)
        try:
            [int(item) for item in value]
        except:
            self._set_error(obj, 'Invalid item type')

class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def perform(self, context, store):
        """ Receive dictionary of clients with their interests  """
        interests = {}

        for client in self.client_ids:
            score = scoring.get_interests(store, client)
            interests['client_%i' % client] = score
        context['nclients'] = len(self.client_ids)

        return interests, 200


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def perform(self, context, store):
        """ Receiving score value for particular data """

        if not ((self.phone and self.email) or
            (self.first_name and self.last_name) or
            (self.birthday and self.gender)):
            raise ValueError({ 'score': 'No correct pairs present' })

        has = []
        response = {
            'score': scoring.get_score(
                store, self.phone, self.email, self.birthday, self.gender,
                self.first_name, self.last_name
            )
        }
        for item in self.fields:
            attr = getattr(self, item)
            if attr: has.append(item)
        context['has'] = has

        return response, 200


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    method = request['body']['method']
    try:
        if method == 'clients_interests':
            request_handler = ClientsInterestsRequest(**request['body']['arguments'])
            response, code = request_handler.perform(ctx, store)
        elif method == 'online_score':
            request_handler = OnlineScoreRequest(**request['body']['arguments'])
            response, code = request_handler.perform(ctx, store)
    except ValueError, e:
        response, code = e.args[0], BAD_REQUEST
    except Exception, e:
        logging.exception("Unexpected error: %s" % e)
        response, code = { 'Unhandled error' }, BAD_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = RedisStore()

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception, e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return

if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
