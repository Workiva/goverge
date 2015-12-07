from unittest import TestCase

from goverge import main


class parse_argsTestCase(TestCase):
    def test_godep(self):
        args = main._parse_args(['--godep'])
        expected = {'godep': True, 'short': False, 'test_path': None}
        self.assertEqual(expected, vars(args))

    def test_short(self):
        args = main._parse_args(['--short'])
        expected = {'godep': False, 'short': True, 'test_path': None}
        self.assertEqual(expected, vars(args))

    def test_path(self):
        args = main._parse_args([
            "--test_path=/foo/bar",
            "--test_path=/bar/foo"
        ])
        expected = {
            'godep': False,
            'short': False,
            'test_path': ['/foo/bar', '/bar/foo']
        }
        self.assertEquals(expected, vars(args))
