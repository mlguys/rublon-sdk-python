from rublon.functions import empty


class RublonConsumer(object):

    """Latest version release of this library."""
    VERSION = '3.7.1'

    """Latest version release date of this library."""
    VERSION_DATE = '2015-07-02'

    """Default API domain."""
    DEFAULT_API_DOMAIN = "https://code.rublon.com"

    """Default technology code name."""
    DEFAULT_TECHNOLOGY = "rublon-php-sdk"

    """Configuration error message template."""
    TEMPLATE_CONFIG_ERROR = 'Before calling Rublon authentication you have to pass the consumer\'s ' \
                            + 'system token and secret key to the Rublon class constructor.'

    def __init__(self, system_token=None, secret_key=None, api_server=None):
        self.system_token = system_token
        self.secret_key = secret_key
        self.api_server = api_server
        self.service_name = ''

    def get_api_domain(self):
        return self.api_server if self.api_server else self.DEFAULT_API_DOMAIN

    def get_lang(self):
        return None

    def get_secret_key(self):
        return self.secret_key

    def get_system_token(self):
        return self.system_token

    def get_technology(self):
        return self.DEFAULT_TECHNOLOGY

    def is_configured(self):
        return not empty(self.system_token) and not empty(self.secret_key)

    def can_user_activate(self):
        return False

    def get_current_url(self):
        # if (!empty($_SERVER['HTTP_HOST'])) {
        # 	$ssl = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] != 'off');
        # 	return ($ssl ? 'https' : 'http') .'://'. $_SERVER['HTTP_HOST'] . (empty($_SERVER['REQUEST_URI']) ? '/' : $_SERVER['REQUEST_URI']);
        # }
        #raise NotImplementedError('Niemozliwe w Pythonie')
        return ''


from rublon.core.html.consumer_script import RublonConsumerScript


class RublonGUI(object):

    def __init__(self, rublon_consumer, user_id=None, user_email=None, logout_listener=False):
        assert isinstance(rublon_consumer, RublonConsumer)
        self.rublon_consumer = rublon_consumer
        self.user_id = user_id
        self.user_email = user_email
        self.logout_listener = logout_listener

    def get_consumer_script(self):
        return str(RublonConsumerScript(self.rublon_consumer, self.user_id, self.user_email, self.logout_listener))

    def get_rublon(self):
        return self.rublon_consumer