import six
import json
from abc import abstractmethod
from rublon.functions import empty
from rublon.core import RublonConsumer, RublonGUI
from rublon.core.auth_params import RublonAuthParams
from rublon.core.signature_wrapper import RublonSignatureWrapper
from rublon.core.api.begin_transaction import RublonAPIBeginTransaction
from rublon.core.api.credentials import RublonApiCredentials
from rublon.core.api.exceptions import UserNotFound_RublonAPIException
from rublon.exceptions import RublonException, RublonConfigurationError, RublonCallbackException
import logging

logging.basicConfig()
logger = logging.getLogger('rublon')


class Rublon2Factor(RublonConsumer):
    """Class provides methods used by `Rublon Two Factor` service process."""

    """Service name."""
    service_name = None

    """Cached credentials."""
    cache_credentials = None

    def __init__(self, *args, **kwargs):
        super(Rublon2Factor, self).__init__(*args, **kwargs)
        self.cache_credentials = {}
        self.service_name = '2factor'

    def auth(self, callback_url, user_id, user_email, extra_params=None):
        """Initializes the Rublon authentication transaction
        and returns the URL address to redirect user's browser
        or NULL if user's account is not protected.

        First, method checks the account's protection status in the Rublon server for current user.
        If user has protected this account, method returns the URL address.
        Redirect user's browser to this URL to start the Rublon authentication process.

        If Rublon user has deleted his Rublon account or Rublon API is not available at this time,
        method returns false. If so, just bypass Rublon and sign in the user.

        Notice: to use this method the configurations values (system token and secret key)
        must be provided to the constructor. If not, function will raise RublonConfigurationError."""

        if extra_params is None:
            extra_params = {}

        if not self.is_configured():
            raise RublonConfigurationError(self.TEMPLATE_CONFIG_ERROR)

        if self.get_lang():
            extra_params['lang'] = self.get_lang()

        try:
            api = RublonAPIBeginTransaction(self, callback_url, user_email, user_id, extra_params)
            api.perform()
            return api.get_web_uri()
        except UserNotFound_RublonAPIException:
            # bypass Rublon
            return None
        except RublonException:
            raise

    def confirm(self, callback_url, user_id, user_email, confirm_message, consumer_params=None):
        """Authenticate user and perform an additional confirmation of the transaction.

        This method requires user to use the Rublon mobile app
        (even if the Trusted Device is available)
        and confirm transaction to maintain higher security level.
        The message passed in the $customMessage argument will be displayed
        in the confirmation dialog on the user's mobile."""
        if consumer_params is None:
            consumer_params = {}

        consumer_params[RublonAuthParams.FIELD_CONFIRM_MESSAGE] = confirm_message
        if self.get_lang():
            consumer_params[RublonAuthParams.FIELD_LANG] = self.get_lang()
        return self.auth(callback_url, user_id, user_email, consumer_params)

    def confirm_with_buffer(self, callback_url, user_id, user_email, confirm_message, time_buffer, consumer_params=None):
        """Perform a confirmation of the transaction without user's action needed
        if the time buffer after previous confirmation has not been reached.

        If the amount of seconds after the previous transaction is less than
        given time buffer, Rublon will confirm the transaction without user's action.
        In other cases, this method will behave the same as the Rublon2Factor::confirm() method."""

        if consumer_params is None:
            consumer_params = {}
        consumer_params[RublonAuthParams.FIELD_CONFIRM_TIME_BUFFER] = time_buffer
        return self.confirm(callback_url, user_id, user_email, confirm_message, consumer_params)

    def get_credentials(self, access_token):
        """Authenticate user and get user's credentials using one-time use
        access token and expected user's profile ID.

        One-time use access token is a session identifier which will be deleted after first usage.
        This method can be called only once in authentication process."""

        if self.cache_credentials.get(access_token):
            # Log
            return self.cache_credentials[access_token]
        else:
            credentials = RublonApiCredentials(self, access_token)
            credentials.perform()
            self.cache_credentials[access_token] = credentials
            return credentials



from rublon.core.html.share_access_widget import RublonShareAccessWidget
from rublon.core.html.device_widget import RublonDeviceWidget


class Rublon2FactorGUI(RublonGUI):
    """Class to create Rublon GUI elements.
    To display the Rublon GUI you can just print the class instance.
    """
    TEMPLATE_BOX_CONTAINER = '<div class="rublon-box" data-configured="{0}" data-can-activate="{1}">{2}</div>{3}{4}'

    def user_box(self):
        """Create user box."""
        return self.get_consumer_script() + self.get_user_box_container()

    def __str__(self):
        """Cast object into string."""
        try:
            return self.user_box()
        except Exception as e:
            #return e.message
            raise

    def get_user_box_container(self, content=''):
        """Get container of the user box."""
        return self.TEMPLATE_BOX_CONTAINER.format(
            int(self.get_rublon().is_configured()),
            int(self.get_rublon().can_user_activate()),
            str(content),
            RublonDeviceWidget(), RublonShareAccessWidget())


from rublon.core.api import RublonAPIClient


class Rublon2FactorCallback(object):
    """Class to handle the Rublon callback action."""

    """State GET parameter name."""
    PARAMETER_STATE = 'state'

    """Access token GET parameter name."""
    PARAMETER_ACCESS_TOKEN = 'token'

    """Custom URI param GET parameter name."""
    PARAMETER_CUSTOM_URI_PARAM = 'custom'

    """Success state value."""
    STATE_OK = 'ok'

    """Error state value."""
    STATE_ERROR = 'error'

    """Logout state value."""
    STATE_LOGOUT = 'logout'

    FIELD_LOGOUT_ACCESS_TOKEN = 'accessToken'
    FIELD_LOGOUT_USER_ID = 'userId'
    FIELD_LOGOUT_DEVICE_ID = 'deviceId'

    """Instance of the Rublon2Factor class"""
    rublon = None

    """Handler to finalize authentication."""
    success_handler = None

    """Handler on cancel."""
    cancel_handler = None

    """Rublon API response instance."""
    credentials = None

    def __init__(self, rublon2factor):
        if not rublon2factor.is_configured():
            raise RublonConfigurationError(rublon2factor.TEMPLATE_CONFIG_ERROR)
        self.rublon = rublon2factor
        self.success_handler = None
        self.cancel_handler = None
        self.credentials = None

    def call(self, success_handler, cancel_handler):
        """Invoke the callback."""
        self.success_handler = success_handler
        self.cancel_handler = cancel_handler

        state = self.get_state().lower()
        if state == self.STATE_OK:
            self.handle_state_ok()
        elif state == self.STATE_ERROR:
            raise RublonCallbackException('Rublon error status.',  RublonCallbackException.ERROR_API_ERROR)
        elif state == self.STATE_LOGOUT:
            self.handle_state_logout()
        else:
            if callable(cancel_handler):
                cancel_handler(self)
            else:
                raise RuntimeError('Cancel handler must be a valid callback.')

    def handle_state_ok(self):
        """Handle state "OK" - run authentication."""
        access_token = self.get_access_token()
        if access_token:
            try:
                self.credentials = self.rublon.get_credentials(access_token)
            except RublonException as e:
                raise RublonCallbackException('Rublon API credentials error.', RublonCallbackException.ERROR_REST_CREDENTIALS, e)

            self.success(self.credentials.get_user_id())
        else:
            raise RublonCallbackException('Missing access token.', RublonCallbackException.ERROR_MISSING_ACCESS_TOKEN)

    def success(self, user_id):
        """Finalize authentication."""
        if self.success_handler is not None and callable(self.success_handler):
            self.success_handler(user_id, self)
        else:
            raise RuntimeError('Success handler must be a valid callback.')

    @abstractmethod
    def get_raw_request_body(self):
        raise NotImplementedError

    def handle_state_logout(self):
        """Handle state logout: parse input and call logout for given user."""
        raw_request_body = self.get_raw_request_body()

        response = {}

        if raw_request_body:
            message = RublonSignatureWrapper.parse_message(raw_request_body, self.rublon.get_secret_key())
            required_fields = [self.FIELD_LOGOUT_ACCESS_TOKEN, self.FIELD_LOGOUT_USER_ID, self.FIELD_LOGOUT_DEVICE_ID]

            for field in required_fields:
                if not message.get(field):
                    response.update({'status': 'ERROR', 'msg': 'Missing field.', 'field': field})
                    break

            if len(response) == 0:
                self.handle_logout(message['userId'], message['deviceId'])
                response.update({'status': 'OK', 'msg': 'Success'})
        else:
            response.update({'status': 'ERROR', 'msg': 'Empty JSON input.'})

        #header('content-type: application/json') ### TODO
        six.print_(json.dumps(response))
        # exit

    def handle_logout(self, user_id, device_id):
        """Handle logout in the local system: logout given user for given deviceId.

        If you want to implement this feature, please override method in a subclass."""
        pass

    @abstractmethod
    def get_state(self):
        """Get state from GET parameters or NULL if not present."""
        raise NotImplementedError

    @abstractmethod
    def get_access_token(self):
        """Get access token from GET parameters or NULL if not present."""
        raise NotImplementedError

    def get_credentials(self):
        """Get the credentials response object."""
        return self.credentials

    def get_consumer_param(self, key):
        """Get consumer param from credentials response."""
        credentials = self.get_credentials()
        if credentials:
            consumer_params = credentials.get_response()
            try:
                consumer_params[RublonAPIClient.FIELD_RESULT][key]
            except KeyError:
                pass


from rublon.core.api.begin_login_transaction import RublonAPIBeginLoginTransaction
from rublon.core.api.login_credentials import RublonAPILoginCredentials


class RublonLogin(RublonConsumer):

    """Service name."""
    service_name = 'native'

    def auth(self, callback_url, consumer_params=None):
        """Get authentication URL."""
        if not self.is_configured():
            raise RublonConfigurationError(self.TEMPLATE_CONFIG_ERROR)

        if consumer_params is None:
            consumer_params = {}

        if self.get_lang():
            consumer_params[RublonAuthParams.FIELD_LANG] = self.get_lang()

        try:
            begin_login_transaction = RublonAPIBeginLoginTransaction(self, callback_url, consumer_params)
            begin_login_transaction.perform()
            return begin_login_transaction.get_web_uri()
        except UserNotFound_RublonAPIException:
            # bypass Rublon
            return None
        except RublonException:
            raise

    def get_credentials(self, access_token):
        credentials = RublonAPILoginCredentials(self, access_token)
        credentials.perform()
        return credentials
