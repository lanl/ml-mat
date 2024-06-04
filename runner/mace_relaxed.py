import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

import pandas as pd
from base import runner
from MACE.calculators import mace_mp
from matbench_discovery.energy import get_e_form_per_atom
from ase.spacegroup import get_spacegroup
from ase import Atoms
from typing import List
import os, parsl

class MACEReduction:
    def reduce(self, rows):
        return pd.DataFrame(rows)

class MACERunner(runner.WrappedAtomsRunner):
    def __init__(self, files: List[str], model_dir: str):
        super(MACERunner, self).__init__(files)
        self.model_dir = model_dir

    def run(self, atoms: Atoms):
        a_copy = atoms.copy()
        calc = mace_mp(model=self.model_dir, dispersion=False, default_dtype="float32", device='cpu')

        atoms.calc = calc
        e_form = get_e_form_per_atom(dict(energy=atoms.get_total_energy(),composition=atoms.get_chemical_formula()))

        return {
            "symbols": atoms.get_chemical_formula(mode='metal'),
            "space-group": get_spacegroup(atoms, symprec=1e-3).no,
            "Atoms": a_copy,
            "E_form": e_form
        }

if __name__ == '__main__':
    parsl.load()

    base_dir = "./files/166_cifs/experimental_lattice_parameters"
    files = [base_dir + "/" + file for file in os.listdir(base_dir)]

    red = MACEReduction()
    run = MACERunner(files, "[[MODEL DIRECTORY]]")

    data_frame = runner.execute_runner(run, red).result()
    print(data_frame)