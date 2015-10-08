import time
import json
import random
from base64 import b64encode

from rublon.functions import hash_data
from rublon.core import RublonConsumer
from rublon.core.auth_params import RublonAuthParams
from rublon.core.signature_wrapper import RublonSignatureWrapper


class RublonConsumerScript(object):
    """Class for generating script tag that embeds consumer's JavaScript library.

    The so-called "consumer script" is an individualized JavaScript library
    that allows the website to use Rublon JavaScript elements - usually
    the Rublon buttons. The library searches Rublon button HTML containers
    in the website's DOM tree and fills them with proper buttons.
    """

    TEMPLATE_SCRIPT = '<script type="text/javascript" src="{0}?t={1}"></script>'
    URL_CONSUMER_SCRIPT = '/native/consumer_script_2factor'

    def __init__(self, rublon_consumer, user_id=None, user_email=None, logout_listener=False):
        assert isinstance(rublon_consumer, RublonConsumer)
        self.rublon_consumer = rublon_consumer
        self.user_id = user_id
        self.user_email = user_email
        self.logout_listener = logout_listener

    def get_consumer_script_url(self):
        """PHP difference - urllib2.urlencode( ) \ """
        return self.rublon_consumer.get_api_domain() + \
            self.URL_CONSUMER_SCRIPT + '/' + \
            b64encode(self.get_params_wrapper()) + '/' + \
            str(random.randint(1, 99999))

    def get_params_wrapper(self):
        """Get signed script input parameters."""
        if self.rublon_consumer.is_configured():
            wrapper = RublonSignatureWrapper()
            wrapper.set_secret_key(self.rublon_consumer.get_secret_key())
            wrapper.set_body(self.get_params())
            return str(wrapper)
        else:
            return json.dumps(self.get_params())

    def get_params(self):
        params = {
            RublonAuthParams.FIELD_ORIGIN_URL : self.rublon_consumer.get_current_url(),
            RublonAuthParams.FIELD_SYSTEM_TOKEN : self.rublon_consumer.system_token,
            RublonAuthParams.FIELD_VERSION : self.rublon_consumer.VERSION_DATE.replace('-', ''),
            RublonAuthParams.FIELD_SERVICE : self.rublon_consumer.service_name
        }

        if self.user_email:
           params[RublonAuthParams.FIELD_USER_EMAIL_HASH] = hash_data(self.user_email, RublonAuthParams.HASH_ALG)

        if self.user_id:
            params[RublonAuthParams.FIELD_USER_ID] = self.user_id

        if self.logout_listener:
            params[RublonAuthParams.FIELD_LOGOUT_LISTENER] = self.logout_listener

        if self.rublon_consumer.get_lang():
            params[RublonAuthParams.FIELD_LANG] = self.rublon_consumer.get_lang()

        return params

    def __str__(self):
        microtime = str(time.time())
        hashed_microtime = hash_data(microtime, 'md5')
        return self.TEMPLATE_SCRIPT.format(self.get_consumer_script_url(), hashed_microtime)

    def __repr__(self):
        return self.__str__()