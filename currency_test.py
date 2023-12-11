import unittest
from currency_query import get_exchange_rate_BOC

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
    
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_get_exchange_rate_BOC(self):
        self.assertIsNotNone(get_exchange_rate_BOC())


if __name__ == '__main__':
    unittest.main()
