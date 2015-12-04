from mock import patch
from subprocess import Popen
import unittest

from goverge.utils import get_package_deps


class TestPackageDeps(unittest.TestCase):

    @patch('goverge.utils.Popen')
    @patch('goverge.utils.Popen.communicate')
    def test_package_deps(self, mock_communicate, mock_popen):
        mock_popen.return_value = Popen
        mock_communicate.return_value = (
            '[foo/bar/a bar/baz foo/bar/b foo/bar/c]', '')

        deps = get_package_deps("foo/bar", ".")

        mock_communicate.assert_called_once()

        self.assertEquals(deps, ["foo/bar/a", "foo/bar/b", "foo/bar/c", "."])
