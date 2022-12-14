import unittest

from main import get_parent_directory

class GetParentDirectoryTestCase(unittest.TestCase):
    def test_get_parent_directory(self):
        # Test with a directory
        path = '/usr/local/bin'
        expected = '/usr/local'
        self.assertEqual(get_parent_directory(path), expected)

        # Test with a file
        path = '/usr/local/bin/python'
        expected = '/usr/local/bin'
        self.assertEqual(get_parent_directory(path), expected)

        # Test with a relative path
        path = '../../bin'
        expected = '../..'
        self.assertEqual(get_parent_directory(path), expected)

if __name__ == '__main__':
    unittest.main()