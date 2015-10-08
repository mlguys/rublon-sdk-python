from . import RublonAPIClient
from rublon.exceptions import RublonConfigurationError


class RublonAPILoginCredentials(RublonAPIClient):
    """API request: Credentials."""

    """Field name for the Rublon profile ID."""
    FIELD_PROFILE_ID = 'profileId'

    """Field name for the Rublon user's email."""
    FIELD_EMAIL_HASH_LIST = 'emailHashList'

    """Field name for the Rublon user's email."""
    FIELD_EMAIL = 'email'

    """Field name for device ID."""
    FIELD_DEVICE_ID = 'deviceId'

    """URL path of the request."""
    url_path = '/api/v3/loginCredentials'

    def __init__(self, rublon_consumer, access_token):
        super(RublonAPILoginCredentials, self).__init__(rublon_consumer)

        if not rublon_consumer.is_configured():
            raise RublonConfigurationError(rublon_consumer.TEMPLATE_CONFIG_ERROR)

        # Set request URL and parameters
        url = rublon_consumer.get_api_domain() + self.url_path
        params = {
            self.FIELD_SYSTEM_TOKEN: rublon_consumer.get_system_token(),
            self.FIELD_ACCESS_TOKEN: access_token
        }
        self.set_request_url(url).set_request_params(params)

    def get_profile_id(self):
        """Get Rublon user's ID."""
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_PROFILE_ID]
        except KeyError:
            return None

    def get_user_email(self):
        """Get Rublon user's email address."""
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_EMAIL]
        except KeyError:
            return None

    def get_user_email_hash_list(self):
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_EMAIL_HASH_LIST]
        except KeyError:
            return None

    def get_device_id(self):
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_DEVICE_ID]
        except KeyError:
            return None
