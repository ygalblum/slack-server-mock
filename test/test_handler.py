import json
import pathlib

from tornado import testing

from slack_server_mock.slack_server.slack_server import start_slack_server, stop_slack_server, SlackServer
from slack_server_mock.injector.di import global_injector


DATA_DIR = pathlib.Path(__file__).parent / 'responses'


class TestBaseSlackHandler(testing.AsyncHTTPTestCase):

    DEFAULT_HEADERS = {
        'Authorization': 'Bearer xoxb-foo',
        'User-Agent': 'python/slackclient/1.3.0'
    }

    def setUp(self):
        super().setUp()
        start_slack_server()
        stop_slack_server()

    def get_app(self):
        return global_injector.get(SlackServer)._http_server._app

    def test_auth_test(self):
        expectation = b'{"ok": false, "error": "invalid_auth"}'
        response = self.fetch('/auth.test')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, expectation)

    def test_conversations_history(self):
        for file in DATA_DIR.glob('conversations.history/*.json'):
            with file.open() as handle:
                expectation = json.load(handle)
            channel, oldest = file.stem.split('-')
            response = self.fetch(f'/conversations.history?channel={channel}&oldest={oldest}',
                                  headers=self.DEFAULT_HEADERS)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
            self.assertDictEqual(json.loads(response.body), expectation)

    def test_conversations_history_404(self):
        expectation = {"ok": False, "error": "channel_not_found"}
        response = self.fetch(f'/conversations.history?channel=c012ab3cd&oldest=12345', headers=self.DEFAULT_HEADERS)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
        self.assertDictEqual(json.loads(response.body), expectation)

    def test_conversations_info(self):
        for file in DATA_DIR.glob('conversations.info/*.json'):
            with file.open() as handle:
                expectation = json.load(handle)
            response = self.fetch(f'/conversations.info?channel={file.stem}', headers=self.DEFAULT_HEADERS)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
            self.assertDictEqual(json.loads(response.body), expectation)

    def test_conversations_info_404(self):
        expectation = {"ok": False, "error": "channel_not_found"}
        response = self.fetch(f'/conversations.info?channel=c12345', headers=self.DEFAULT_HEADERS)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
        self.assertDictEqual(json.loads(response.body), expectation)

    def test_conversations_replies(self):
        for file in DATA_DIR.glob('conversations.replies/*.json'):
            with file.open() as handle:
                expectation = json.load(handle)
            channel, ts = file.stem.split('-')
            response = self.fetch(f'/conversations.replies?channel={channel}&ts={ts}', headers=self.DEFAULT_HEADERS)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
            self.assertDictEqual(json.loads(response.body), expectation)

    def test_conversations_replies_404(self):
        expectation = {"ok": False, "error": "thread_not_found"}
        response = self.fetch(f'/conversations.replies?channel=c12345&ts=1234', headers=self.DEFAULT_HEADERS)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
        self.assertDictEqual(json.loads(response.body), expectation)

    def test_users_info(self):
        for file in DATA_DIR.glob('users.info/*.json'):
            with file.open() as handle:
                expectation = json.load(handle)
            response = self.fetch(f'/users.info?user={file.stem}', headers=self.DEFAULT_HEADERS)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
            self.assertDictEqual(json.loads(response.body), expectation)

    def test_users_info_404(self):
        expectation = {"ok": False, "error": "user_not_found"}
        response = self.fetch(f'/users.info?user=w12345', headers=self.DEFAULT_HEADERS)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json; charset=UTF-8')
        self.assertDictEqual(json.loads(response.body), expectation)
