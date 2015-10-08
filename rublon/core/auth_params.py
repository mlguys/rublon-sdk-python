class RublonAuthParams(object):

    """Hash algorithm name to compute the user's email hash."""
    HASH_ALG = 'sha256'

    """Field name for access token parameter."""
    FIELD_ACCESS_TOKEN = "accessToken"

    """Name of the field with profile ID."""
    FIELD_PROFILE_ID = 'profileId'

    """Field name for "service" parameter"""
    FIELD_SERVICE = "service"

    """Field name for "systemToken" parameter"""
    FIELD_SYSTEM_TOKEN = "systemToken"

    """Field name for origin URL."""
    FIELD_ORIGIN_URL = "originUrl"

    """Field name for language parameter"""
    FIELD_LANG = "lang"

    """Field name for window type."""
    FIELD_WINDOW_TYPE = 'windowType'

    """Field name for return URL."""
    FIELD_RETURN_URL = 'returnUrl'

    """Field name for consumer parameters"""
    FIELD_CONSUMER_PARAMS = "consumerParams"

    """Field name for callback URL."""
    FIELD_CALLBACK_URL = 'callbackUrl'

    """Field name for local user ID."""
    FIELD_USER_ID = "userId"

    """Field name for local user email address."""
    FIELD_USER_EMAIL_HASH = "userEmailHash"

    """Field name for logout listener boolean flag."""
    FIELD_LOGOUT_LISTENER = "logoutListener"

    """Field name for required Rublon user's profile ID."""
    FIELD_REQUIRE_PROFILE_ID = "requireProfileId"

    """Field name for action flag."""
    FIELD_ACTION_FLAG = "actionFlag"

    """Field name for version parameter."""
    FIELD_VERSION = "version"

    """Field name to require Rublon to authenticate
    by mobile app only, not using Email 2-factor."""
    FIELD_FORCE_MOBILE_APP = 'forceMobileApp'

    """Field name to force ignoring the existing Trusted Device
    during the authentication."""
    FIELD_IGNORE_TRUSTED_DEVICE = 'ignoreTrustedDevice'

    """Field name to add a custom URI query parameter to the callback URL."""
    FIELD_CUSTOM_URI_PARAM = 'customURIParam'

    """Field name to define a message for a transaction."""
    FIELD_CONFIRM_MESSAGE = 'confirmMessage'

    """Field name to set the time buffer in seconds from previous confirmation
    which allow Rublon to confirm the custom transaction
    without user's action."""
    FIELD_CONFIRM_TIME_BUFFER = 'confirmTimeBuffer'

    """URL path to authentication code"""
    URL_PATH_CODE = "/code/native/"

    """Action flag for login action."""
    ACTION_FLAG_LOGIN = 'login'

    """Action flag for enable protection action."""
    ACTION_FLAG_LINK_ACCOUNTS = 'link_accounts'

    """Action flag for disable protection action."""
    ACTION_FLAG_UNLINK_ACCOUNTS = 'unlink_accounts'