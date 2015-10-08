import re
from . import RublonAPIClient
from rublon.exceptions import RublonConfigurationError, RublonException


class RublonApiCredentials(RublonAPIClient):
    """API request: Credentials."""

    """Invalid access token error."""
    ERROR_ACCESS_TOKEN = 'Invalid access token.'

    """Field name with the additional confirmation result."""
    FIELD_CONFIRM_RESULT = 'answer'

    """Field name for the Rublon profile ID."""
    FIELD_PROFILE_ID = 'profileId'

    """Field name for the Rublon user's email."""
    FIELD_EMAIL = 'email'

    """Field name for device ID."""
    FIELD_DEVICE_ID = 'deviceId'

    """User pressed the "Yes" button on the additional confirmation of the transaction."""
    CONFIRM_RESULT_YES = 'true'

    """User pressed the "No" button on the additional confirmation of the transaction."""
    CONFIRM_RESULT_NO = 'false'

    """URL path of the request."""
    url_path = '/api/v3/credentials'

    def __init__(self, rublon_consumer, access_token):
        """
        :type rublon_consumer RublonConsumer
        """
        super(RublonApiCredentials, self).__init__(rublon_consumer)

        if not rublon_consumer.is_configured():
            raise RublonConfigurationError(rublon_consumer.TEMPLATE_CONFIG_ERROR)

        if re.match(r'[a-zA-Z0-9]{100}', access_token) is None:
            raise RublonException(self.ERROR_ACCESS_TOKEN, RublonException.CODE_INVALID_ACCESS_TOKEN)

        self.response = {}

        # Set request URL and parameters
        url = rublon_consumer.get_api_domain() + self.url_path
        params = {
            self.FIELD_SYSTEM_TOKEN: rublon_consumer.get_system_token(),
            self.FIELD_ACCESS_TOKEN: access_token

        }
        self.set_request_url(url).set_request_params(params)

    def get_user_id(self):
        """Get local user's ID."""
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_USER_ID]
        except KeyError:
            return None

    def get_confirm_result(self):
        """Get the additional confirmation of the transaction result.

        Method returns a result only if the Rublon2Factor::confirm()
        method was used to initialize the auth transaction."""

        try:
            return self.response[self.FIELD_RESULT][self.FIELD_CONFIRM_RESULT]
        except KeyError:
            return None

    def get_profile_id(self):
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_PROFILE_ID]
        except KeyError:
            return None

    def get_user_email(self):
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_EMAIL]
        except KeyError:
            return None

    def get_device_id(self):
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_DEVICE_ID]
        except KeyError:
            return None