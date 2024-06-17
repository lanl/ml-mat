import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

from base_execution import execute_runner
from parsl import python_app
import os

from configs import configs
import pandas as pd

def reduce(rows):
    print("Reducing")
    return pd.DataFrame(rows)

@python_app
def execute_single(atoms, model_dir):
    from matbench_discovery.energy import get_e_form_per_atom
    from ase.spacegroup import get_spacegroup
    from mace.calculators import mace_mp

    a_copy = atoms.copy()
    calc = mace_mp(model=model_dir, dispersion=False, default_dtype="float64", device='cpu')

    atoms.calc = calc
    e_form = get_e_form_per_atom(dict(energy=atoms.get_total_energy(),composition=atoms.get_chemical_formula()))

    return {
        "symbols": atoms.get_chemical_formula(mode='metal'),
        "space-group": get_spacegroup(atoms, symprec=1e-3).no,
        "Atoms": a_copy,
        "E_form": e_form
    }

if __name__ == "__main__":
    # skylake-gold takes 55 seconds with 5 nodes

    base_dir = "./files/166_cifs/substituted_and_relaxed_structure_types"
    files = [base_dir + "/" + file for file in os.listdir(base_dir)]
    data_frame = execute_runner(configs["darwin"], execute_single, reduce, files, "./files/models/2024-01-07-mace-128-L2_epoch-199.model")
    data_frame.to_pickle("data.pd")
    print(data_frame)
