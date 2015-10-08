import re
import os
import os.path
import six
import hmac
import json
import pycurl
import hashlib
if six.PY3:
    from io import BytesIO as StringIO
else:
    from StringIO import StringIO

from rublon.exceptions import RublonException

import rublon.core.api.exceptions
from rublon.core.api.exceptions import InvalidResponse_RublonClientException, EmptyResponse_RublonClientException, \
    InvalidJSON_RublonClientException, MissingField_RublonClientException, ErrorResponse_RublonClientException, \
    InvalidSignature_RublonClientException, MissingHeader_RublonClientException, RublonAPIException, \
    RublonClientException


def make_http_header(name, value):
    return '{0}: {1}'.format(name, value)


class RublonAPIClient(object):

    """Connection timeout in seconds."""
    TIMEOUT = 30

    """Hash algorithm name to compute the user's email hash."""
    HASH_ALG = 'sha256'

    """User agent string."""
    USER_AGENT = 'rublon-php-sdk'

    """HTTP Content-type header."""
    HEADER_CONTENT_TYPE = "Content-Type: application/json"

    """HTTP Accept header."""
    HEADER_ACCEPT = "Accept: application/json, text/javascript, */*; q=0.01"

    """HTTP Expect header."""
    HEADER_EXPECT = "Expect: 200-OK"

    HEADER_TECHNOLOGY = "X-Rublon-Technology"
    HEADER_SIGNATURE = 'X-Rublon-Signature'
    HEADER_API_VERSION = 'X-Rublon-API-Version'
    HEADER_API_VERSION_DATE = 'X-Rublon-API-Version-Date'
    FIELD_ACCESS_TOKEN = 'accessToken'
    FIELD_SYSTEM_TOKEN = 'systemToken'
    FIELD_USER_EMAIL_HASH = 'userEmailHash'
    FIELD_USER_ID = 'userId'
    FIELD_CALLBACK_URL = 'callbackUrl'
    FIELD_STATUS = 'status'
    FIELD_RESULT = 'result'
    FIELD_ERROR_MSG = 'errorMessage'
    FIELD_EXCEPTION = 'exception'
    FIELD_NAME = 'name'
    FIELD_USING_EMAIL2FA = 'usingEmail2FA'
    FIELD_ACCESS_CONTROL_MANAGER_ALLOWED = 'accessControlManagerAllowed'
    STATUS_OK = 'OK'
    STATUS_ERROR = 'ERROR'

    """Path to the pem certificates."""
    PATH_CERT = os.path.join(os.path.dirname(__file__), '..', '..', 'cert/cacert.pem')

    def __init__(self, rublon_consumer):
        self.rublon_consumer = rublon_consumer
        self.response = {
            self.FIELD_RESULT: {}
        }
        self.raw_post_body = None
        self.request_params = {}
        self.response_http_status = None
        self.response_http_status_code = None
        self.response_headers = {}

    def perform(self):
        self._perform_request()
        try:
            self._validate_response()
        except RublonException:
            raise

        return self

    def _validate_response(self):
        if str(self.response_http_status_code) != '200':
            raise InvalidResponse_RublonClientException(self,
                                  'Unexpected response HTTP status code: {0}'.format(self.response_http_status_code))
        if not self.raw_response_body:
            raise EmptyResponse_RublonClientException(self, 'Empty response body.')
        try:
            self.response = json.loads(self.raw_response_body)
        except ValueError:
            raise InvalidJSON_RublonClientException(self)

        if not self.response.get(self.FIELD_STATUS):
            raise MissingField_RublonClientException(self, self.FIELD_STATUS)

        if self.response[self.FIELD_STATUS] == self.STATUS_OK:
            signature = self.response_headers.get(self.HEADER_SIGNATURE)
            if signature:
                if self._validate_signature(signature, self.raw_response_body):
                    return True
                else:
                    raise InvalidSignature_RublonClientException(self, 'Invalid response signature: {0}'.format(signature))
            else:
                raise MissingHeader_RublonClientException(self, self.HEADER_SIGNATURE)
        elif self.response[self.FIELD_STATUS] == self.STATUS_ERROR:
            if not self.response.get(self.FIELD_RESULT):
                raise ErrorResponse_RublonClientException(self, 'Server returns empty result.')
            if self.response[self.FIELD_RESULT].get(self.FIELD_EXCEPTION):
                raise self._construct_exception(self.response[self.FIELD_RESULT])
            elif self.response[self.FIELD_RESULT].get(self.FIELD_ERROR_MSG):
                raise ErrorResponse_RublonClientException(self, self.response[self.FIELD_RESULT][self.FIELD_ERROR_MSG])
            else:
                raise ErrorResponse_RublonClientException(self, 'Server returns error status with empty error message.')
        else:
            raise InvalidResponse_RublonClientException(self, 'Invalid status field: {0}'.format(self.response[self.FIELD_STATUS]))

    def _construct_exception(self, result_field):
        class_name = result_field[self.FIELD_EXCEPTION]
        if not hasattr(rublon.core.api.exceptions, class_name) or \
                not issubclass(getattr(rublon.core.api.exceptions, class_name), RublonAPIException):
            class_name = 'RublonAPIException'

        if result_field.get(self.FIELD_NAME):
            arg = result_field[self.FIELD_NAME]
        elif result_field.get(self.FIELD_ERROR_MSG):
            arg = result_field[self.FIELD_ERROR_MSG]
        else:
            arg = None

        return getattr(rublon.core.api.exceptions, class_name)(self, arg)

    def set_request_params(self, params):
        assert isinstance(params, dict)
        self.request_params = params
        return self

    def add_request_params(self, params):
        assert isinstance(params, dict)
        self.request_params.update(params)
        return self

    def set_request_url(self, url):
        self.url = url
        return self

    def get_response(self):
        return self.response

    def get_raw_response(self):
        return self.raw_response

    def _perform_request(self):
        """Perform a request and set rawResponse field."""
        if not self.raw_post_body and self.request_params is not None:
            self.raw_post_body = json.dumps(self.request_params)

        response = self._request()
        self.raw_response = ''.join(response)

        self.raw_response_header = response.pop(0).strip()
        self.raw_response_body = response.pop(0).strip()

        headers = self.raw_response_header.split('\n')
        self.response_http_status = headers.pop(0)
        match = re.match(r'^HTTP/\d\.\d (\d+)', self.response_http_status)
        if match is not None:
            self.response_http_status_code = match.group(1)

        for header in [h for h in headers if ':' in h]:
            name, value = header.split(':', 1)
            self.response_headers[name.strip()] = value.strip()

    def _request(self):
        response_buffer = StringIO()

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self.url)
        headers = [
            self.HEADER_CONTENT_TYPE,
            self.HEADER_ACCEPT,
            self.HEADER_EXPECT,
            make_http_header(self.HEADER_SIGNATURE, self._sign_message(self.raw_post_body)),
            make_http_header(self.HEADER_TECHNOLOGY, self.rublon_consumer.get_technology()),
            make_http_header(self.HEADER_API_VERSION, self.rublon_consumer.VERSION),
            make_http_header(self.HEADER_API_VERSION_DATE, self.rublon_consumer.VERSION_DATE)
        ]
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.TIMEOUT, self.TIMEOUT)
        curl.setopt(pycurl.CONNECTTIMEOUT, self.TIMEOUT)
        curl.setopt(pycurl.HEADER, True)
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
        curl.setopt(pycurl.USERAGENT, self.USER_AGENT)

        if self.raw_post_body:
            curl.setopt(pycurl.POST, True)
            curl.setopt(pycurl.POSTFIELDS, self.raw_post_body)

        curl.setopt(pycurl.SSL_VERIFYPEER, True)
        curl.setopt(pycurl.SSL_VERIFYHOST, 2)
        curl.setopt(pycurl.CAINFO, self.PATH_CERT)
        curl.perform()

        response = response_buffer.getvalue()
        if six.PY3:
            response = response.decode('utf-8')

        error = curl.errstr()
        if error:
            curl.close()
            raise RublonClientException(self, error)
        else:
            header_size = curl.getinfo(pycurl.HEADER_SIZE)
            header = response[:header_size]
            body = response[header_size:]
            curl.close()
            return [header, body]

    def _sign_message(self, data, secret=None):
        if secret is None:
            secret = self.rublon_consumer.secret_key
        if six.PY3:
            data = data.encode('utf-8')
            secret = bytes(secret, 'utf-8')

        return hmac.new(secret, data, getattr(hashlib, self.HASH_ALG)).hexdigest()

    def _validate_signature(self, signature, data, secret=None):
        check = self._sign_message(data, secret)
        return check == signature
