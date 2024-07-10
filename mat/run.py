import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

import time

from base_execution import execute_runner
from parsl import python_app
import os, json, argparse

from configs import configs
import pandas as pd

# ----------- Reductions -----------

def reduce(rows):
    print("Reducing")
    return pd.DataFrame(rows)

reductions = { "pandas_reduce": reduce }

# ----------- Runners -----------

@python_app
def execute_mace(atoms, model_dir):
    from matbench_discovery.energy import get_e_form_per_atom
    from ase.spacegroup import get_spacegroup
    from mace.calculators import mace_mp
    from ase.optimize import BFGS
    from ase.constraints import ExpCellFilter

    a_copy = atoms.copy()
    atoms.calc = mace_mp(model=model_dir["model"], dispersion=False, default_dtype="float32", device='cpu')
    relaxed = ExpCellFilter(atoms)
    opt = BFGS(relaxed)
    opt.run(fmax=1e-4)
    atoms_relaxed = relaxed.atoms

    e_form = get_e_form_per_atom(dict(energy=atoms_relaxed.get_total_energy(),composition=atoms_relaxed.get_chemical_formula()))

    return {
        "symbols": a_copy.get_chemical_formula(mode='metal'),
        "space-group": get_spacegroup(a_copy, symprec=1e-3).no,
        "Atoms": a_copy,
        "E_form": e_form
    }

runners = { "mace": execute_mace }

def load_config(filename):
    return json.loads(open(filename, "r").read())

def execute_config(config, parsl_config = None):
    executors = []
    for d in config["executions"]:
        executors.append(( runners[d["runner"]], reductions[d["reduction"]] ))

    files = [config["base_dir"] + "/" + file for file in os.listdir(config["base_dir"])]
    if "max_inputs" in config:
        files = files[:config["max_inputs"]]

    start_time = time.time()

    data_frame = execute_runner(configs[config["parsl_config"]] if parsl_config is None else parsl_config, executors, files, config["args"])
    print(data_frame[0])
    
    print("Writing dataframe to out.tar")
    data_frame[0].to_pickle("out.tar")

    print("------- done in %s seconds -------", time.time() - start_time)
    return data_frame, time.time() - start_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Parallel Run",
        description="A simple scheme parallelizing indepdent algorithms")
    parser.add_argument("-c", "--config", default="./files/configs/basic_run.json", help="Configuration file to execute")
    args = parser.parse_args()

    print("Executing configuration file '" + args.config + "'...")
    execute_config(load_config(args.config))