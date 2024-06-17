import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

from base_execution import execute_runner
from parsl import python_app
import os, sys, json

from configs import configs
import pandas as pd

def reduce(rows):
    print("Reducing")
    return pd.DataFrame(rows)

reductions = { "pandas_reduce": reduce }

@python_app
def execute_mace(atoms, model_dir):
    from matbench_discovery.energy import get_e_form_per_atom
    from ase.spacegroup import get_spacegroup
    from mace.calculators import mace_mp

    a_copy = atoms.copy()
    calc = mace_mp(model=model_dir["model"], dispersion=False, default_dtype="float64", device='cpu')

    atoms.calc = calc
    e_form = get_e_form_per_atom(dict(energy=atoms.get_total_energy(),composition=atoms.get_chemical_formula()))

    return {
        "symbols": atoms.get_chemical_formula(mode='metal'),
        "space-group": get_spacegroup(atoms, symprec=1e-3).no,
        "Atoms": a_copy,
        "E_form": e_form
    }

runners = { "mace": execute_mace }

if __name__ == "__main__":
    # skylake-gold takes 55 seconds with 5 nodes
    config_file = ""
    if len(sys.argv) == 1:
        config_file = "./files/configs/basic_run.json"
    else:
        config_file = sys.argv[1]
    
    config = json.loads(open(config_file, "r").read())

    executors = []
    for d in config["executions"]:
        executors.append(( runners[d["runner"]], reductions[d["reduction"]] ))

    files = [config["base_dir"] + "/" + file for file in os.listdir(config["base_dir"])]
    data_frame = execute_runner(configs[config["parsl_config"]], executors, files, config["args"])
    #data_frame.to_pickle("data.pd")
    print(data_frame[0])
