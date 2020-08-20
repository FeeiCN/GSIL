import unittest
from gsil.notification import Notification


class TestNotification(unittest.TestCase):
    def test_notification(self):
        subject = 'test from GSIL'
        to = cc = 'feei@feei.cn'
        html = '<h1>Test Content from GSIL</h1>'
        self.assertTrue(Notification(subject, to, cc).notification(html))


if __name__ == '__main__':
    unittest.main()
