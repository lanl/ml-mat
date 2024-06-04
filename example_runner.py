import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

from runner.base import runner, reduction
import parsl, unittest
from ase import Atoms
from typing import Union, List

class ExampleRunner(runner.WrappedAtomsRunner):
    def __init__(self, file_location: str):
        super(ExampleRunner, self).__init__(file_location)

    def run(self, atoms: Union[Atoms, List[Atoms]]):
        print(str(atoms))

class RunnerTest(unittest.TestCase):
    def setUp(self):
        parsl.load()
        
    def tearDown(self):
        parsl.clear()

    def test_run(self):
        red = reduction.TestReduction()
        run = ExampleRunner(["test_file", "what"])

        fut = runner.execute_runner(run, red)
        self.assertTrue(fut.result())
        
if __name__ == '__main__':
    unittest.main()