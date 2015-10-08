from . import RublonAPIClient
from rublon.exceptions import RublonConfigurationError


class RublonAPICheckUserDevice(RublonAPIClient):
    """API request: CheckUserDevice."""

    FIELD_PROFILE_ID = 'profileId'
    FIELD_DEVICE_ID = 'deviceId'
    FIELD_DEVICE_STATUS = 'deviceActive'

    """URL path of the request."""
    url_path = '/api/v3/checkUserDevice'

    def __init__(self, rublon_consumer, profile_id, device_id):
        super(RublonAPICheckUserDevice, self).__init__(rublon_consumer)

        if not rublon_consumer.is_configured():
            raise RublonConfigurationError(rublon_consumer.TEMPLATE_CONFIG_ERROR)

        # Set request URL and parameters
        self.set_request_url(rublon_consumer.get_api_domain() + self.url_path)
        self.set_request_params({
            self.FIELD_PROFILE_ID: profile_id,
            self.FIELD_DEVICE_ID: device_id
        })

    def perform(self):
        self.add_request_params({
            self.FIELD_SYSTEM_TOKEN: self.rublon_consumer.get_system_token()
        })
        return super(RublonAPICheckUserDevice, self).perform()

    def is_device_active(self):
        """Check if device is active."""
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_DEVICE_STATUS]
        except KeyError:
            pass
