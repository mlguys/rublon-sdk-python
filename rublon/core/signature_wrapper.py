import json
import random
import hmac
import time
import hashlib
import six
import logging

logger = logging.getLogger('rublon')
from rublon.exceptions import RublonException


class RublonSignatureWrapper(object):
    """Signature wrapper for input and output data.

    Body of the message is signed by the HMAC-SHA256 hash of the string formed of
    concatenation of the consumer's secret key and the body string.
    Body and its signature are wrapped into a JSON structure.

    To verify the input message it's necessary to compute the HMAC-SHA256 hash
    of the consumer's secret key concatenated with the message body string
    and compare with the signature of the message.
    """

    """Rublon message life time"""
    MESSAGE_LIFETIME = 300

    """Hash algorithm name for HMAC."""
    HASH_ALG = 'SHA256'

    """Field name for wrapper data."""
    FIELD_DATA = 'data'

    """Field name for message body."""
    FIELD_BODY = 'body'

    """Field name for message header."""
    FIELD_HEAD = 'head'

    """Field name for size."""
    FIELD_HEAD_SIZE = 'size'

    """Field name for time."""
    FIELD_HEAD_TIME = 'time'

    """Field name for signature."""
    FIELD_SIGN = 'sign'

    """Field name for status."""
    FIELD_STATUS = 'status'

    """Field name for message content"""
    FIELD_MSG = 'msg'

    """Error status."""
    STATUS_ERROR = 'ERROR'

    """Config key to skip time validation."""
    CONFIG_SKIP_TIME = 'skipTime'

    def __init__(self):
        self.secret_key = None
        self.body = None
        self.raw_data = None

    def __str__(self):
        """Get object's string - JSON with signed data."""
        return json.dumps(self.get_wrapper())

    def __repr__(self):
        return self.__str__()

    def set_input(self, input):
        """Set raw input."""
        self.raw_data = input
        decoded = json.loads(input)
        if self.FIELD_DATA in decoded:
            if not isinstance(decoded[self.FIELD_DATA], dict):
                data = json.loads(decoded[self.FIELD_DATA])
            else:
                data = decoded[self.FIELD_DATA]

            if self.FIELD_BODY in data:
                if not isinstance(data[self.FIELD_BODY], dict):
                    self.body = json.loads(data[self.FIELD_BODY])
                else:
                    self.body = data[self.FIELD_BODY]
            else:
                self.body = None
        else:
            self.body = None

    def set_secret_key(self, secret_key):
        """Sets secret key."""
        self.secret_key = secret_key

    def set_body(self, body):
        self.body = body

    def get_body(self):
        """Get body data."""
        return self.body

    def get_wrapper(self):
        """Get wrapper with data and signature generated from body."""
        return self.wrap(self.secret_key, self.body)

    @classmethod
    def verify_data(cls, data, secret_key, sign):
        """Verify data by signature and secret key."""
        data_sign = cls.sign_data(data, secret_key)
        return data_sign == sign

    @classmethod
    def sign_data(cls, data, secret_key):
        """Sign data by secret key."""
        if six.PY3:
            data = data.encode('utf-8')
            secret_key = bytes(secret_key, 'utf-8')

        return hmac.new(secret_key, data, getattr(hashlib, cls.HASH_ALG.lower())).hexdigest()

    @classmethod
    def wrap(cls, secret_key, body):
        """Wrap string message into wrapper with signature."""
        if not isinstance(body, six.string_types):
            try:
                body = json.dumps(body)
            except ValueError:
                body = None
                raise
                logger.log(logger.WARNING, 'Could not decode body, setting None')

        data = json.dumps({
            cls.FIELD_HEAD: {
                cls.FIELD_HEAD_SIZE: len(body),
                cls.FIELD_HEAD_TIME: int(time.time())
            },
            cls.FIELD_BODY: body
        })

        return {
            cls.FIELD_DATA: data,
            cls.FIELD_SIGN: cls.sign_data(data, secret_key)
        }

    @classmethod
    def parse_message(cls, json_str, secret_key, config=None):
        """Parses signed message."""
        if config is None:
            config = {}

        if not secret_key:
            raise RublonException('Empty secret')

        if not json_str:
            raise RublonException('Empty response', RublonException.CODE_INVALID_RESPONSE)

        # Verify response json
        try:
            response = json.loads(json_str)
        except ValueError:
            raise RublonException('Invalid response: {0}'.format(json_str), RublonException.CODE_INVALID_RESPONSE)

        if response.get(cls.FIELD_STATUS) and response[cls.FIELD_STATUS] == cls.STATUS_ERROR:
            msg = response[cls.FIELD_STATUS] if response.get(cls.FIELD_MSG) else 'Error response: {0}'.format(json_str)
            raise RublonException(msg, RublonException.CODE_INVALID_RESPONSE)

        if not response.get(cls.FIELD_SIGN):
            raise RublonException('Missing sign field', RublonException.CODE_INVALID_RESPONSE)

        if not response.get(cls.FIELD_DATA):
            raise RublonException('Missing data field', RublonException.CODE_INVALID_RESPONSE)

        if not cls.verify_data(response[cls.FIELD_DATA], secret_key, response[cls.FIELD_SIGN]):
            raise RublonException('Invalid signature', RublonException.CODE_INVALID_RESPONSE)

        # Verify data field
        try:
            data = json.loads(response[cls.FIELD_DATA])
        except ValueError:
            raise RublonException('Invalid response', RublonException.CODE_INVALID_RESPONSE)

        if not data.get(cls.FIELD_HEAD) or not isinstance(data[cls.FIELD_HEAD], dict):
            raise RublonException('Invalid response data (invalid header)', RublonException.CODE_INVALID_RESPONSE)

        # Verify head field
        head = data[cls.FIELD_HEAD]
        if not config.get(cls.CONFIG_SKIP_TIME) and not (head.get(cls.FIELD_HEAD_TIME) and
                abs(time.time() - int(head.get(cls.FIELD_HEAD_TIME))) <= cls.MESSAGE_LIFETIME):
            raise RublonException('Invalid message time', RublonException.CODE_TIMESTAMP_ERROR)

        # Verify body field
        if not data.get(cls.FIELD_BODY) or not isinstance(data[cls.FIELD_BODY], six.string_types):
            raise RublonException('Invalid response data (no body)', RublonException.CODE_INVALID_RESPONSE)

        try:
            body = json.loads(data[cls.FIELD_BODY])
        except ValueError:
            body = None
        if body and isinstance(body, dict):
            return body
        else:
            return data[cls.FIELD_BODY]

    @classmethod
    def generate_random_string(self, length=100):
        alphabet = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
        return ''.join(random.choice(alphabet) for _ in range(length))