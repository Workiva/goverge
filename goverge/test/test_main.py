from unittest import TestCase

from goverge import main


class parse_argsTestCase(TestCase):
    def test_godep(self):
        args = main._parse_args(['--godep'])
        expected = {
            'godep': True,
            'html': False,
            'project_import': None,
            'short': False,
            'test_path': None
        }
        self.assertEqual(expected, vars(args))

    def test_html(self):
        args = main._parse_args(["--html"])
        expected = {
            'godep': False,
            'html': True,
            'project_import': None,
            'short': False,
            'test_path': None
        }
        self.assertEquals(expected, vars(args))

    def test_short(self):
        args = main._parse_args(['--short'])
        expected = {
            'godep': False,
            'html': False,
            'project_import': None,
            'short': True,
            'test_path': None
        }
        self.assertEqual(expected, vars(args))

    def test_path(self):
        args = main._parse_args([
            "--test_path=/foo/bar",
            "--test_path=/bar/foo"
        ])
        expected = {
            'godep': False,
            'html': False,
            'project_import': None,
            'short': False,
            'test_path': ['/foo/bar', '/bar/foo']
        }
        self.assertEquals(expected, vars(args))

    def test_project_import(self):
        args = main._parse_args([
            "--project_import=github.com/Workiva/goverge"
        ])
        expected = {
            'godep': False,
            'html': False,
            'project_import': "github.com/Workiva/goverge",
            'short': False,
            'test_path': None
        }
        self.assertEquals(expected, vars(args))
