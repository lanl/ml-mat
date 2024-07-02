import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

import time

from base_execution import execute_runner
from parsl import python_app
import os, sys, json, argparse

from configs import configs, get_local
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
    from ase.phonons import Phonons

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

    print("------- done in %s seconds -------", time.time() - start_time)
    return data_frame, time.time() - start_time


# ---------- Optimizeing algorithm ----------
def optimize():
    config = load_config("./files/configs/opt_run.json")
    
    data = {"data": []}
    for blocks in range(1, 20, 2):
        for parallel_int in range(2, 10):
            _, time = execute_config(config, parsl_config=get_local(blocks, parallel_int / 10.0))
            data["data"].append((blocks, parallel_int / 10.0, time))
    
    min = 100000000
    best_time = None
    for d in data["data"]:
        if d[2] < min: 
            min = d[2]
            best_time = d
    open("out.txt", "w").write(json.dumps({ "best_config": best_time }))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Parallel Run",
        description="A simple scheme parallelizing indepdent algorithms")
    parser.add_argument("-c", "--config", default="./files/configs/basic_run.json", help="Configuration file to execute")
    parser.add_argument("-e", "--execute_config", action='store_true', help="Execute the given configuration file")
    parser.add_argument("-o", "--optimize", action='store_true', help="Run the local parsl config optimization algorithm")
    args = parser.parse_args()

    if args.execute_config and args.optimize: print("Cannot perform optimization and execution in the same run...")
    else:
        if args.execute_config: 
            print("Executing configuration file '" + args.config + "'...")
            execute_config(load_config(args.config))
        elif args.optimize:       
            print("Optimizing local configuration...")
            optimize()
        else: parser.print_usage()

    #config_file = ""
    #if len(sys.argv) == 1:
    #    config_file = "./files/configs/basic_run.json"
    #else:
    #    config_file = sys.argv[1]
    
    #execute_config(load_config(config_file))