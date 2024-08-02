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
    import signal
    
    from pymatgen.core import Composition
    from pymatgen.io.ase import AseAtomsAdaptor
    from pymatgen.ext.matproj import MPRester 
    from pymatgen.analysis.phase_diagram import PhaseDiagram
    from ase.optimize import BFGS
    from ase.constraints import ExpCellFilter
    import glob

    def get_decompostion_product_energy(Atoms,calculator, return_composition=False):
        element_set = set(Atoms.get_chemical_symbols())
        chemical_formula = Atoms.get_chemical_formula()
        #The API key here is my account (shunl@lanl.gov) 
        with MPRester("F255Sg0ysObKbsUlzvFHRJhlQ8YXMJpY") as mpr:

        # Obtain only corrected GGA and GGA+U ComputedStructureEntry objects
            entries = mpr.get_entries_in_chemsys(elements=element_set, 
                                            additional_criteria={"thermo_types": ["GGA_GGA+U"]}) 
        # Construct phase diagram
            pd = PhaseDiagram(entries)
        comp = Composition(chemical_formula)
        decomp = pd.get_decomposition(comp)
        sum = 0
        decomposition_product = []
        calc = calculator
        #Use ASE Calculator to predict formation energy of decomposition compounds
        for item in decomp.items():
            pdentry = item[0].structure
            fraction = item[1]
            #convert to ase Atoms objects
            atoms = AseAtomsAdaptor.get_atoms(pdentry,msonable=False)
            atoms.calc = calc
            #get formation energy, change this line if you want to use a calculator that can predict formation energy directly.
            e_form = get_e_form_per_atom(dict(energy=atoms.get_total_energy(),composition=atoms.get_chemical_formula()))
            sum += e_form * fraction
            decomposition_product.append([atoms.get_chemical_formula(),fraction,e_form])
        # print(atoms.symbols)
        if return_composition:
            return decomposition_product, sum
        else:
            return sum
    
    a_copy = atoms.copy()

    ret = {
        "symbols": a_copy.get_chemical_formula(mode='metal'),
        "space-group": get_spacegroup(a_copy, symprec=1e-3).no,
        "Atoms": a_copy,
        "E_form": float('nan'),
        "E_above_hull": float('nan')
    }
    
    # We set up a signal here so that it will throw this exception when the signal is sent
    def signal_handler(signum, frame):
        raise Exception("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(int(60 * 60 * 2.5))   # 4 hours per task
    try:
        # Run the mace calculator for formation energy
        atoms.calc = mace_mp(model=model_dir["model"], dispersion=False, default_dtype="float32", device='cpu')
        relaxed = ExpCellFilter(atoms)
        opt = BFGS(relaxed)
        opt.run(fmax=1e-4)
        atoms_relaxed = relaxed.atoms

        e_form = get_e_form_per_atom(dict(energy=atoms_relaxed.get_total_energy(),composition=atoms_relaxed.get_chemical_formula()))
        ret["E_form"] = e_form

        # Next calculate the energy above hull
        _, sum = get_decompostion_product_energy(atoms_relaxed, calculator=atoms.calc, return_composition=True)
        ret["E_above_hull"] = e_form - sum

    except Exception as ex:
        print(str(ex))

    # If either formation energy is not set or E_above_hull they will be NaN

    return ret

@python_app
def execute_vasp(atoms):
    pass

runners = { "mace": execute_mace, "vasp": execute_vasp }

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

    print("------- done in", time.time() - start_time, "seconds -------")
    return data_frame, time.time() - start_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Parallel Run",
        description="A simple scheme parallelizing indepdent algorithms")
    parser.add_argument("-c", "--config", default="./files/configs/basic_run.json", help="Configuration file to execute")
    args = parser.parse_args()

    print("Executing configuration file '" + args.config + "'...")
    execute_config(load_config(args.config))
