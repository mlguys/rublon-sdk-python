from . import RublonAPIClient
from rublon.functions import empty
from rublon.exceptions import RublonConfigurationError
from rublon.core.api.exceptions import MissingField_RublonClientException


class RublonAPIBeginLoginTransaction(RublonAPIClient):
    """API request: BeginLoginTransaction."""

    URL_PATH = '/api/v3/beginLoginTransaction'

    FIELD_SYSTEM_TOKEN = 'systemToken'
    FIELD_CALLBACK_URL = 'callbackUrl'
    FIELD_WEB_URI = 'webURI'

    def __init__(self, rublon_consumer, callback_url, consumer_params=None):
        if consumer_params is None:
            consumer_params = {}

        super(RublonAPIBeginLoginTransaction, self).__init__(rublon_consumer)

        if not rublon_consumer.is_configured():
            raise RublonConfigurationError(rublon_consumer.TEMPLATE_CONFIG_ERROR)

        consumer_params.update({
            self.FIELD_SYSTEM_TOKEN: rublon_consumer.get_system_token(),
            self.FIELD_CALLBACK_URL: callback_url
        })

        # Set request URL and parameters
        url = rublon_consumer.get_api_domain() + self.URL_PATH
        self.set_request_url(url).set_request_params(consumer_params)

    def get_web_uri(self):
        """Returns URI to redirect to."""
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_WEB_URI]
        except KeyError:
            return None

    def _validate_response(self):
        if super(RublonAPIBeginLoginTransaction, self)._validate_response():
            if self.FIELD_WEB_URI in self.response[self.FIELD_RESULT] and \
                    not empty(self.response[self.FIELD_RESULT][self.FIELD_WEB_URI]):
                return True
            else:
                raise MissingField_RublonClientException(self, self.FIELD_WEB_URI)