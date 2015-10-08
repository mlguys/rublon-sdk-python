from rublon.functions import hash_data
from rublon.core.auth_params import RublonAuthParams
from rublon.exceptions import RublonConfigurationError
from rublon.core.api.exceptions import MissingField_RublonClientException
from . import RublonAPIClient


class RublonAPIBeginTransaction(RublonAPIClient):
    URL_PATH = '/api/v3/beginTransaction'
    FIELD_USER_ID = 'userId'
    FIELD_USER_EMAIL_HASH = 'userEmailHash'
    FIELD_USER_EMAIL = 'userEmail'
    FIELD_SYSTEM_TOKEN = 'systemToken'
    FIELD_CALLBACK_URL = 'callbackUrl'
    FIELD_WEB_URI = 'webURI'

    def __init__(self, rublon_consumer, callback_url, user_email, user_id, consumer_params):
        super(RublonAPIBeginTransaction, self).__init__(rublon_consumer)

        if not rublon_consumer.is_configured():
            raise RublonConfigurationError('')

        consumer_params[self.FIELD_SYSTEM_TOKEN] = rublon_consumer.system_token
        consumer_params[self.FIELD_USER_ID] = user_id
        consumer_params[self.FIELD_USER_EMAIL_HASH] = hash_data(user_email, self.HASH_ALG)
        if not consumer_params.get(RublonAuthParams.FIELD_FORCE_MOBILE_APP):
            consumer_params[self.FIELD_USER_EMAIL] = user_email.lower()
        consumer_params[self.FIELD_CALLBACK_URL] = callback_url

        url = rublon_consumer.get_api_domain() + self.URL_PATH
        self.set_request_url(url)
        self.set_request_params(consumer_params)

    def get_web_uri(self):
        return self.response[self.FIELD_RESULT][self.FIELD_WEB_URI]

    def _validate_response(self):
        if super(RublonAPIBeginTransaction, self)._validate_response():
            if self.response[self.FIELD_RESULT].get(self.FIELD_WEB_URI):
                return True
            else:
                raise MissingField_RublonClientException(self, self.FIELD_WEB_URI)