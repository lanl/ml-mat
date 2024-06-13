import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

from base import runner
from ase import Atoms
from ase.spacegroup import get_spacegroup
from typing import List
import pandas as pd
import os, parsl

class PandasReduction:
    def reduce(self, rows):
        return pd.DataFrame(rows)

class PandasRunner(runner.WrappedAtomsRunner):
    def __init__(self, files: List[str]):
        super(PandasRunner, self).__init__(files)

    def run(self, atoms: Atoms):
        return {
            "symbols": atoms.get_chemical_formula(mode='metal'),
            "space-group": get_spacegroup(atoms, symprec=1e-3).no,
            "Atoms": atoms,
        }

if __name__ == '__main__':
    parsl.load()

    base_dir = "./files/166_cifs/substituted_and_relaxed_structure_types"
    files = [base_dir + "/" + file for file in os.listdir(base_dir)]

    red = PandasReduction()
    run = PandasRunner(files)

    data_frame = runner.execute_runner(run, red).result()
    print(data_frame)