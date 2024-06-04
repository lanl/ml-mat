import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

import parsl, unittest
from parsl import python_app
from config import getConfig

@python_app
def pi(n: int):
    from random import random

    inside: int = 0
    for i in range(n):
        x, y = random(), random()
        if x**2 + y**2 < 1:
            inside += 1
    
    return inside * 4 / n

@python_app
def mean(values: list):
    return sum(values) / len(values)

class ParslMonteCarlo(unittest.TestCase):
    def setUp(self):
        parsl.load(getConfig())

    def test_montecarlo(self):
        N = 10000
        n = 5000
        futures = [ pi(n) for i in range(N) ]
        outputs = [ f.result() for f in futures ]
        approx = mean(outputs).result()

        self.assertAlmostEqual(3.14159, approx, 3)

if __name__ == '__main__':
    unittest.main()