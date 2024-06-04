import unittest

# Simple tests to test the tester...
class TestMethods(unittest.TestCase):
    def test_a(self):
        self.assertEqual(2 + 2, 4)

    def test_b(self):
        self.assertFalse(2 + 2 == 3)

if __name__ == '__main__':
    unittest.main()