from rublon.exceptions import RublonException


"""Client exceptions"""


class RublonClientException(RublonException):
    def __init__(self, client, message=None):
        super(RublonClientException, self).__init__(message)
        self.client = client


class RublonClientResponseException(RublonClientException):
    pass


class InvalidSignature_RublonClientException(RublonClientResponseException):
    pass


class MissingField_RublonClientException(RublonClientResponseException):
    def __init__(self, client, item_name):
        message = '[ {0} ] {1}'.format(self.__class__.__name__, item_name)
        super(MissingField_RublonClientException, self).__init__(client, message)
        self.item_name = item_name


class MissingHeader_RublonClientException(MissingField_RublonClientException):
    pass


class ErrorResponse_RublonClientException(RublonClientResponseException):
    pass


class EmptyResponse_RublonClientException(RublonClientResponseException):
    pass


class InvalidResponse_RublonClientException(RublonClientResponseException):
    pass


class InvalidJSON_RublonClientException(InvalidResponse_RublonClientException):
    pass


"""Api exceptions"""


class RublonAPIException(RublonException):
    def __init__(self, client, message):
        super(RublonAPIException, self).__init__(message)
        self.client = client


class MissingField_RublonAPIException(RublonAPIException):
    def __init__(self, client, item_name):
        message = '[ {0} ] {1}'.format(self.__class__.__name__, item_name)
        super(MissingField_RublonAPIException, self).__init__(client, message)
        self.item_name = item_name


class MissingHeader_RublonAPIException(MissingField_RublonAPIException):
    pass


class UnsupportedRequestMethod_RublonAPIException(RublonAPIException):
    pass


class EmptyInput_RublonAPIException(RublonAPIException):
    pass


class InvalidJSON_RublonAPIException(RublonAPIException):
    pass


class InvalidSignature_RublonAPIException(RublonAPIException):
    pass


class ConsumerNotFound_RublonAPIException(RublonAPIException):
    pass


class UnsupportedVersion_RublonAPIException(RublonAPIException):
    pass


class UserNotFound_RublonAPIException(RublonAPIException):
    pass


class AccessTokenExpired_RublonAPIException(RublonAPIException):
    pass


class UnknownAccessToken_RublonAPIException(RublonAPIException):
    pass


class SessionRestore_RublonAPIException(RublonAPIException):
    pass


class UnauthorizedUser_RublonAPIException(RublonAPIException):
    pass


class ForbiddenMethod_RublonAPIException(RublonAPIException):
    pass


class PersonalEditionLimited_RublonApiException(RublonAPIException):
    pass