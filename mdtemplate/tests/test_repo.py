import unittest

from ..utils.repo import Repository


class RepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self._repo = Repository()

    @unittest.mock.patch("subprocess.check_output")
    def test_git_cloned_by_https(self, mock_url):
        mock_url.return_value = b"https://github.com/jcwillox/md-template.git\n"

        self._repo.load_url()

        self.assertEqual(self._repo.name, "md-template")
        self.assertEqual(self._repo.owner, "jcwillox")

    @unittest.mock.patch("subprocess.check_output")
    def test_git_cloned_by_ssh(self, mock_url):
        mock_url.return_value = b"git@github.com:jcwillox/md-template.git\n"

        self._repo.load_url()

        self.assertEqual(self._repo.name, "md-template")
        self.assertEqual(self._repo.owner, "jcwillox")
