import unittest
import datetime
import uuid
import sys
import os

base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, os.pardir))

from pypushwoosh import client
from pypushwoosh import constants
from pypushwoosh.command import CreateTargetedMessageCommand, CreateMessageForApplicationCommand, \
    CreateMessageForApplicationGroupCommand, DeleteMessageCommand, CompileFilterCommand, RegisterDeviceCommand, \
    UnregisterDeviceCommand, SetBadgeCommand, SetTagsCommand, GetNearestZoneCommand
from pypushwoosh.filter import ApplicationFilter
from pypushwoosh.notification import Notification
from pypushwoosh.exceptions import PushwooshCommandException, PushwooshNotificationException

HTTP_200_OK = 200
STATUS_OK = 'OK'


class TestCreateMessageCommand(unittest.TestCase):

    def setUp(self):
        self.client = client.PushwooshClient()
        self.notification = Notification()
        self.notification.content = 'Hello world!'
        self.auth = os.environ.get('PW_TOKEN')

    def test_valid_create_by_application(self):
        self.command = CreateMessageForApplicationCommand(self.notification,
                                                          application=os.environ.get('PW_APP_CODE'))
        self.command.auth = self.auth
        response = self.client.invoke(self.command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)
        self.assertEqual(True, 'Messages' in response['response'])

    def test_valid_create_by_application_group(self):
        self.command = CreateMessageForApplicationGroupCommand(self.notification,
                                                               application_group=os.environ.get('PW_APP_GROUP_CODE'))
        self.command.auth = self.auth
        response = self.client.invoke(self.command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)
        self.assertEqual(True, 'Messages' in response['response'])

    def test_create_message_without_application(self):
        self.command = CreateMessageForApplicationCommand(self.notification)
        self.command.auth = self.auth
        self.assertRaises(PushwooshCommandException, self.command.compile)

    def test_create_message_without_application_group(self):
        self.command = CreateMessageForApplicationGroupCommand(self.notification)
        self.command.auth = self.auth
        self.assertRaises(PushwooshCommandException, self.command.compile)


class TestCreateTargetedMessageCommand(unittest.TestCase):

    def setUp(self):
        self.client = client.PushwooshClient()
        self.command = CreateTargetedMessageCommand()
        self.command.auth = os.environ.get('PW_TOKEN')
        self.command.content = "Hello world!"

    def test_valid_create(self):
        self.command.devices_filter = ApplicationFilter(os.environ.get('PW_APP_CODE'))
        response = self.client.invoke(self.command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)
        self.assertEqual(True, 'messageCode' in response['response'])

    def test_create_without_device_filter(self):
        self.assertRaises(PushwooshNotificationException, self.command.compile)


class TestDeleteMessageCommand(unittest.TestCase):

    def setUp(self):
        self.client = client.PushwooshClient()
        self.command = DeleteMessageCommand()

    def get_message(self):
        command = CreateTargetedMessageCommand()
        command.auth = os.environ.get('PW_TOKEN')
        command.content = "Hello world!"
        command.devices_filter = ApplicationFilter(os.environ.get('PW_APP_CODE'))
        tomorrow = datetime.datetime.today() + datetime.timedelta(1)
        command.send_date = tomorrow.strftime('%Y-%m-%d %H:%M:%S')
        response = self.client.invoke(command)
        return response['response']['messageCode']

    def test_valid_delete(self):
        self.command.auth = os.environ.get('PW_TOKEN')
        self.command.message = self.get_message()
        response = self.client.invoke(self.command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)


class TestCompileFilterCommand(unittest.TestCase):

    def setUp(self):
        self.client = client.PushwooshClient()
        self.command = CompileFilterCommand()

    def test_valid_compile_filter(self):
        self.command.auth = os.environ.get('PW_TOKEN')
        self.command.devices_filter = ApplicationFilter(os.environ.get('PW_APP_CODE'))
        response = self.client.invoke(self.command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)
        self.assertEqual(True, 'devices_count' in response['response'])


class TestDeviceCommands(unittest.TestCase):

    def setUp(self):
        self.client = client.PushwooshClient()
        self.auth = os.environ.get('PW_TOKEN')
        self.hwid = str(uuid.uuid4())
        self.push_token = str(uuid.uuid4())
        self.app_code = os.environ.get('PW_APP_CODE')

        # Register device for tests
        command = RegisterDeviceCommand(self.app_code, self.hwid, constants.PLATFORM_ANDROID, self.push_token)
        self.client.invoke(command)

    def test_valid_register_device(self):
        command = RegisterDeviceCommand(self.app_code, self.hwid, constants.PLATFORM_ANDROID, self.push_token)
        response = self.client.invoke(command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)

    def test_valid_set_tag_command(self):
        command = SetTagsCommand(self.app_code, self.hwid, {'testtag': 'test'})
        response = self.client.invoke(command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)

    def test_valid_set_badge_command(self):
        command = SetBadgeCommand(self.app_code, self.hwid, 5)
        response = self.client.invoke(command)

        self.assertEqual(response['status_message'], 'Badges can be set on iOS devices only')

    def test_get_nearest_zone_command(self):
        lat = '53.42513'
        lng = '83.92817'
        command = GetNearestZoneCommand(self.app_code, self.hwid, lat, lng)
        response = self.client.invoke(command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)

    def test_valid_unregister_device(self):
        command = UnregisterDeviceCommand(self.app_code, self.hwid)
        response = self.client.invoke(command)

        self.assertEqual(response['status_code'], HTTP_200_OK)
        self.assertEqual(response['status_message'], STATUS_OK)


if __name__ == '__main__':
    unittest.main()