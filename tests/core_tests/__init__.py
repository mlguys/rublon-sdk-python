from ..import RublonTestBase
from nose.tools import assert_not_equals, assert_equals, assert_raises
from mock import Mock, patch
import json

from rublon.exceptions import RublonException
from rublon.core.signature_wrapper import RublonSignatureWrapper


class RublonSignatureWrapperTests(RublonTestBase):

    def setUp(self):
        self.signature_wrapper = RublonSignatureWrapper()

    def test_set_input_correct_json(self):
        input_data = '{"data":{"body":{"bodyfield": 1}}}'
        self.signature_wrapper.set_input(input_data)
        assert_equals(1, self.signature_wrapper.body['bodyfield'])

    def test_nested_encoded_json(self):
        level_body = json.dumps({'bodyfield': 1})
        level_data = json.dumps({'body': level_body})
        input_data = json.dumps({'data': level_data})
        self.signature_wrapper.set_input(input_data)
        assert_equals(1, self.signature_wrapper.body['bodyfield'])

    def test_set_secret_key(self):
        self.signature_wrapper.set_secret_key(secret_key='secret')
        assert_equals('secret', self.signature_wrapper.secret_key)

    def test_set_get_body(self):
        body = {'bodyfield': 1}
        self.signature_wrapper.set_body(body)
        assert_equals(body, self.signature_wrapper.get_body())

    def test_get_wrapper(self):
        self.signature_wrapper.set_secret_key('secret')
        self.signature_wrapper.set_body({'bodyfield': 1})
        result = self.signature_wrapper.get_wrapper()
        assert isinstance(result, dict)
        assert 'data' in result
        assert 'sign' in result

    def test_verify_data_different_keys(self):
        data = json.dumps({'bodyfield': 1})
        sign1 = self.signature_wrapper.sign_data(data, 'secret1')
        sign2 = self.signature_wrapper.sign_data(data, 'secret2')
        assert_not_equals(sign1, sign2)

    def test_verify_data_different_data_sets(self):
        data1 = json.dumps({'bodyfield': 1})
        data2 = json.dumps({'bodyfield': 5})
        sign1 = self.signature_wrapper.sign_data(data1, 'secret')
        sign2 = self.signature_wrapper.sign_data(data2, 'secret')
        assert_not_equals(sign1, sign2)

    def test_verify_data_equals(self):
        data = json.dumps({'bodyfield': 1})
        sign1 = self.signature_wrapper.sign_data(data, 'secret')
        sign2 = self.signature_wrapper.sign_data(data, 'secret')
        assert_equals(sign1, sign2)

    def test_parse_message_raises_exceptions_when_given_empty_secret_key(self):
        assert_raises(RublonException, self.signature_wrapper.parse_message, '{}', '')

    def test_parse_message_raises_exceptions_when_given_empty_json_str(self):
        assert_raises(RublonException, self.signature_wrapper.parse_message, '', 'secret')

    def test_parse_message_raises_exception_when_given_invalid_json(self):
        assert_raises(RublonException, self.signature_wrapper.parse_message, 'lalal', 'secret')

    def test_parse_message_raises_exception_when_error_status_and_empty_field_message(self):
        json_str = '{"status": "ERROR"}'
        try:
            self.signature_wrapper.parse_message(json_str, 'secret')
            self.fail('RublonException was not raised!')
        except RublonException as e:
            assert_equals('Error response: {0}'.format(json_str), e.message)

    def test_parse_message_raises_exception_when_error_status_and_not_empty_field_message(self):
        json_str = '{"status": "ERROR", "msg": "something", "data":"{}", "sign":"somesign"}'
        try:
            self.signature_wrapper.parse_message(json_str, 'secret')
            self.fail('RublonException was not raised!')
        except RublonException as e:
            assert_equals('ERROR', e.message)

    def test_parse_message_raises_exception_when_there_is_no_data_field(self):
        json_str = '{"status":"OK", "sign":"sign"}'
        assert_raises(RublonException, self.signature_wrapper.parse_message, json_str, 'secret')

    def test_parse_message_raises_exception_when_there_is_no_sign_field(self):
        json_str = '{"status":"OK", "data":"{}"}'
        assert_raises(RublonException, self.signature_wrapper.parse_message, json_str, 'secret')

    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=False))
    def test_parse_messages_raises_exception_if_invalid_signature(self):
        json_str = '{"status":"OK", "data":"{}", "sign":"somesign"}'
        try:
            self.signature_wrapper.parse_message(json_str, 'secret')
            self.fail('RublonException was not raised!')
        except RublonException as e:
            assert 'Invalid signature' in e.message

    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=True))
    def test_parse_message_raises_exception_if_data_malformed(self):
        json_str = '{"status":"OK", "data":"malformed_json", "sign":"somesign"}'
        assert_raises(RublonException, self.signature_wrapper.parse_message, json_str, 'secret')

    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=True))
    def test_parse_message_raises_exception_if_no_head_in_data_present(self):
        json_str = '{"status":"OK", "data":"{}", "sign":"somesign"}'
        try:
            self.signature_wrapper.parse_message(json_str, 'secret')
            self.fail('RublonException was not raised!')
        except RublonException as e:
            assert 'invalid header' in e.message

    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=True))
    def test_parse_message_raises_exception_if_head_time_required_and_absent(self):
        data = json.dumps({'head': {'sth': 'else'}})
        json_str = json.dumps({"status": "OK", "data": data, "sign":"somesign"})
        try:
            self.signature_wrapper.parse_message(json_str, 'secret')
            self.fail('RublonException was not raised!')
        except RublonException as e:
            assert_equals('Invalid message time', e.message)
            assert_equals(RublonException.CODE_TIMESTAMP_ERROR, e.code)

    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=True))
    def test_parse_message_raises_exception_if_head_time_and_very_old(self):
        data = json.dumps({'head': {'time': 100}})
        json_str = json.dumps({"status": "OK", "data": data, "sign":"somesign"})
        try:
            self.signature_wrapper.parse_message(json_str, 'secret')
            self.fail('RublonException was not raised!')
        except RublonException as e:
            assert_equals('Invalid message time', e.message)
            assert_equals(RublonException.CODE_TIMESTAMP_ERROR, e.code)


    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=True))
    def test_parse_message_raises_exception_if_body_absent(self):
        config = {'skipTime': True}
        data = json.dumps({'head': {'sth': 'else'}})
        json_str = json.dumps({"status": "OK", "data": data, "sign":"somesign"})
        try:
            self.signature_wrapper.parse_message(json_str, 'secret', config)
            self.fail('RublonException was not raised!')
        except RublonException as e:
            assert_equals('Invalid response data (no body)', e.message)
            assert_equals(RublonException.CODE_INVALID_RESPONSE, e.code)

    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=True))
    def test_parse_message_returns_body_if_it_is_a_string(self):
        config = {'skipTime': True}
        data = json.dumps({'head': {'sth': 'else'}, 'body': 'somestring'})
        json_str = json.dumps({"status": "OK", "data": data, "sign":"somesign"})
        result = self.signature_wrapper.parse_message(json_str, 'secret', config)
        assert_equals('somestring', result)

    @patch.object(RublonSignatureWrapper, 'verify_data', Mock(return_value=True))
    def test_parse_message_returns_body_if_it_is_a_json(self):
        config = {'skipTime': True}
        data = json.dumps({'head': {'sth': 'else'}, 'body': json.dumps({'key': 'value'})})
        json_str = json.dumps({"status": "OK", "data": data, "sign":"somesign"})
        result = self.signature_wrapper.parse_message(json_str, 'secret', config)
        assert isinstance(result, dict)
        assert_equals(result['key'], 'value')

    def test_generating_random_string(self):
        str1 = RublonSignatureWrapper.generate_random_string()
        str2 = RublonSignatureWrapper.generate_random_string()
        assert_not_equals(str1, str2)