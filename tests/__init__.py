import unittest

from mock import patch, Mock
import os
from nose.tools import assert_raises, assert_equals
from rublon import Rublon2Factor
from rublon.core.api.begin_transaction import RublonAPIBeginTransaction
from rublon.exceptions import RublonConfigurationError
from rublon.core.api.exceptions import RublonAPIException


RESPONSE_HEADERS = '''HTTP/1.1 200 OK
Server: nginx
Date: Sun, 16 Aug 2015 20:31:36 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
Set-Cookie: rublon_code_session=a%3A5%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22ea1264f4f674e566d167310b44d24e96%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A13%3A%2231.183.25.166%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A14%3A%22rublon-php-sdk%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1439757096%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3B%7D2b702b8ed8d25d26a602adde6df92b00; path=/; secure; httponly
Expires: Sat, 26 Jul 1997 05:00:00 GMT
Last-Modified: Sun, 16 Aug 2015 20:31:36 GMT
Cache-Control: no-store, no-cache, must-revalidate
Cache-Control: post-check=0, pre-check=0
Pragma: no-cache
X-Rublon-Signature: 8119fdcec0a5e7cdf7a8a571bbd8579a1f7aa77086d942846063e77101962552
X-Rublon-API-Version: 3.7.0
X-Rublon-API-Version-Date: 2014-05-20
Strict-Transport-Security: max-age=2592000
'''

ERROR_BODY_PERSONAL_LIMITED = '{"status": "ERROR", "result": {"exception": "PersonalEditionLimited_RublonApiException", "errorMessage": "You have logged in successfully, but due the Personal Edition limitation your account isn\'t protected by Rublon and thus vulnerable to password theft and brute force attacks. Upgrade to the Business Edition needed (<a href=\\"mailto:sales@rublon.com\\">sales@rublon.com</a>). Please contact your administrator."}}'
AUTHORIZED_BODY = ''''{"status":"OK","result":{"webURI":"https:\\/\\/code.rublon.com\\/api\\/v3\\/web\\/Tk2V4R56MQ1q94AucnpTpdVMx9NJJW63g3zWYNQOzfbLjgOr26om6newBR2llcVb2AEd6wnuSIDp5yx3gGlZVPo9mROmyGbpV7rx"}}'''


def get_rublon_api_begin_transaction_fake():
    class RublonAPIBeginTransactionFake(object):
        pass

    RublonAPIBeginTransactionFake.__init__ = Mock(return_value=None)
    RublonAPIBeginTransactionFake.get_web_uri = Mock()
    RublonAPIBeginTransactionFake.perform = Mock()

    return RublonAPIBeginTransactionFake


class RublonTestBase(unittest.TestCase):
    system_token = os.getenv('RUBLON_TEST_SYSTEM_TOKEN')
    secret_key = os.getenv('RUBLON_TEST_SECRET_KEY')
    protected_email = os.environ['RUBLON_TEST_PROTECTED_EMAIL']
    invalid_email = os.environ['RUBLON_TEST_INVALID_EMAIL']
    callback_url = os.environ['RUBLON_TEST_CALLBACK_URL']
    own_user_id = 1

    def get_rublon2factor(self):
        return Rublon2Factor(system_token=self.system_token, secret_key=self.secret_key)


class Rublon2FactorAuthTests(RublonTestBase):

    def setUp(self):
        self.rublon = self.get_rublon2factor()

    def test_email_not_under_rublon_raises_rublon_api_exception_url(self):
        with patch('rublon.RublonAPIBeginTransaction', RublonAPIBeginTransaction):
            RublonAPIBeginTransaction._request = lambda _: [RESPONSE_HEADERS, ERROR_BODY_PERSONAL_LIMITED]
            assert_raises(RublonAPIException, self.rublon.auth, self.callback_url, self.own_user_id, self.invalid_email)

    def test_email_under_rublon_gives_concrete_url(self):
        fake_class = get_rublon_api_begin_transaction_fake()
        with patch('rublon.RublonAPIBeginTransaction', fake_class):
            fake_class._request = lambda: [RESPONSE_HEADERS, AUTHORIZED_BODY]
            result = self.rublon.auth(callback_url=self.callback_url, user_id=self.own_user_id, user_email=self.protected_email)
        assert result.startswith('https://code.rublon.com/api/v3/web/'), 'invalid URL!'

    def test_incorrectly_configured_rublon2factor_raises_exception(self):
        rublon = Rublon2Factor(system_token=None, secret_key=None)
        assert_raises(RublonConfigurationError, rublon.auth, self.callback_url, self.own_user_id, self.protected_email)

    def test_get_lang_returns_not_empty_then_is_appended_to_extra_params(self):
        extra_params = {}
        fake_class = get_rublon_api_begin_transaction_fake()
        self.rublon.get_lang = lambda: 'Not_empty'
        with patch('rublon.RublonAPIBeginTransaction', fake_class):  # substitute imported class
            self.rublon.auth(callback_url=self.callback_url, user_id=self.own_user_id, user_email=self.protected_email,
                             extra_params=extra_params)
        assert_equals(self.rublon.get_lang(), extra_params['lang'])

    def test_creates_RublonAPIBeginTransaction(self):
        fake_class = get_rublon_api_begin_transaction_fake()
        with patch('rublon.RublonAPIBeginTransaction', fake_class):  # substitute imported class
            self.rublon.auth(callback_url=self.callback_url, user_id=self.own_user_id, user_email=self.protected_email)
        fake_class.__init__.assert_called_once_with(self.rublon, self.callback_url, self.protected_email, self.own_user_id, {})
        fake_class.perform.assert_called_once_with()
        fake_class.get_web_uri.assert_called_once_with()


class RublonAPIBeginTransactionTests(RublonTestBase):

    def setUp(self):
        consumer = self.get_rublon2factor()
        self.api = RublonAPIBeginTransaction(rublon_consumer=consumer, callback_url=self.callback_url,
                                             user_email=self.protected_email, user_id=self.own_user_id,
                                             consumer_params={})

    def test_raises_error_if_given_consumer_is_not_set_up(self):
        consumer = Rublon2Factor()
        assert_raises(RublonConfigurationError, RublonAPIBeginTransaction, consumer, self.callback_url,
                      self.protected_email, self.own_user_id, {})


class Rublon2FactorGuiTests(RublonTestBase):

    def setUp(self):
        pass
