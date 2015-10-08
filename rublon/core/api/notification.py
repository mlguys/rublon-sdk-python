from . import RublonAPIClient
from rublon.exceptions import RublonConfigurationError


class RublonAPINotification(RublonAPIClient):
    """API request: Notification."""

    FIELD_NOTIFICATION_CHANNEL = 'channel'
    FIELD_NOTIFICATION_TITLE = 'title'
    FIELD_NOTIFICATION_URL = 'url'
    FIELD_NOTIFICATION_TYPE = 'type'
    TYPE_URL = 'URL'

    url_path = '/api/v3/notification'

    def __init__(self, rublon_consumer):
        super(RublonAPINotification, self).__init__(rublon_consumer)

        if not rublon_consumer.is_configured():
            raise RublonConfigurationError(rublon_consumer.TEMPLATE_CONFIG_ERROR)

        self.notification_channel = None
        self.notification_title = None
        self.notification_url = None
        self.notification_type = None

        self.set_request_url(rublon_consumer.get_api_domain() + self.url_path)

    def perform(self):
        self.add_request_params({
            self.FIELD_SYSTEM_TOKEN: self.rublon_consumer.get_system_token(),
            self.FIELD_NOTIFICATION_CHANNEL: self.notification_channel,
            self.FIELD_NOTIFICATION_TITLE: self.notification_title,
            self.FIELD_NOTIFICATION_URL: self.notification_url,
            self.FIELD_NOTIFICATION_TYPE: self.notification_type
        })
        return super(RublonAPINotification, self).perform()

    def set_notification_channel(self, channel):
        self.notification_channel = channel
        return self

    def set_notification_title(self, title):
        self.notification_title = title
        return self

    def set_notification_url(self, url):
        self.notification_url = url
        return self

    def set_notification_type(self, type):
        self.notification_type = type

    def init_url_notification(self, title, url):
        self.set_notification_type(self.TYPE_URL)
        self.set_notification_title(title)
        self.set_notification_url(url)