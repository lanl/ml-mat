import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

import parsl, unittest
from parsl import python_app

@python_app
def run_test(number):
    return number * 3

class ParslTest(unittest.TestCase):
    def setUp(self):
        parsl.load()
        
    def tearDown(self):
        parsl.clear()

    def test_run(self):
        self.assertEqual(run_test(2).result(), 6)