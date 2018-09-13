from mock import patch
from subprocess import Popen
from unittest import TestCase

from goverge.packages import get_sub_packages
from goverge.packages import get_project_package


class TestPackageTestCase(TestCase):

    @patch('goverge.packages.os.walk')
    def test_get_sub_packages(self, mock_os_walk):
        mock_os_walk.return_value = [
            ("/foo/bar/Godeps", ('',), ("foo")),
            ("/foo/bar/vendor/", ('',), ("foo")),
            ("/./foo", ('',), ("foo")),
            ("/foo/bar/", ('',), ("foo")),
            ("/foo/bar/baz", ('',), ("foo")),
            ("/foo/bar/ignore", ('',), ("foo")),
        ]

        test_packages = get_sub_packages(
            test_path=None,
            project_root="/foo/bar/",
            ignore_list=["/foo/bar/ignore"]
        )
        self.assertEqual(test_packages, ["/foo/bar/", "/foo/bar/baz"])
        mock_os_walk.assert_called_once_with("/foo/bar/")

    @patch('goverge.packages.Popen')
    @patch('goverge.packages.Popen.communicate')
    def test_get_project_package(self, mock_comm, mock_popen):
        mock_popen.return_value = Popen
        mock_comm.return_value = "'foo/bar'", ""
        package = get_project_package("/test/foo/bar", "")
        self.assertEquals(package, "foo/bar")