from . import RublonAPIClient
from rublon.exceptions import RublonConfigurationError, RublonException


class RublonAPIGetAvailableFeatures(RublonAPIClient):
    """API request: GetAvailableFeatures."""

    FIELD_FEATURES = 'features'

    FEATURE_FORCE_MOBILE_APP = 'forceMobileApp'
    FEATURE_IGNORE_TRUSTED_DEVICE = 'ignoreTrustedDevice'
    FEATURE_OPERATION_CONFIRMATION = 'operationConfirmation'
    FEATURE_BUFFERED_CONFIRMATION = 'bufferedAutoConfirmation'
    FEATURE_IDENTITY_PROVIDING = 'accessControlManager'
    FEATURE_REMOTE_LOGOUT = 'remoteLogout'

    """URL path of the request."""
    url_path = '/api/v3/getAvailableFeatures'

    def __init__(self, rublon_consumer):
        super(RublonAPIGetAvailableFeatures, self).__init__(rublon_consumer)

        if not rublon_consumer.is_configured():
            raise RublonConfigurationError(rublon_consumer.TEMPLATE_CONFIG_ERROR)

        self.set_request_url(rublon_consumer.get_api_domain() + self.url_path)

    def perform(self):
        self.add_request_params({
            self.FIELD_SYSTEM_TOKEN: self.rublon_consumer.get_system_token()
        })
        return super(RublonAPIGetAvailableFeatures, self).perform()

    def get_features(self):
        try:
            return self.response[self.FIELD_RESULT][self.FIELD_FEATURES]
        except KeyError:
            return None


