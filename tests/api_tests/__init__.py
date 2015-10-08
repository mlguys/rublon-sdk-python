from .. import RublonTestBase
from nose.tools import assert_raises
from rublon.core.api.credentials import RublonApiCredentials
from rublon.core.api.exceptions import UnknownAccessToken_RublonAPIException


class RublonApiCredentialsTests(RublonTestBase):

    def test_raises_invalid_access_token_exception(self):
        consumer = self.get_rublon2factor()
        credentials = RublonApiCredentials(consumer, 'a' * 100)
        assert_raises(UnknownAccessToken_RublonAPIException, credentials.perform)
