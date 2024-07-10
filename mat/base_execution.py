import time
from ase import io
import parsl

class Base:
    def __init__(self, files):
        self.files = files

    def open_file(self):
        for file_loc in self.files:
            try:
                yield io.read(file_loc), True
            except Exception as e:
                yield "Error reading file: " + str(e), False

def execute_runner(config, run_red_list, files, dict_list):  
    parsl.load(config)

    r = Base(files)
    print("Executing runner...")

    # We want to parse the CIF files in parallel...
    runs = [[] for r in range(len(run_red_list))]
    for atoms, success in r.open_file():
        if not success:
            # In the case of failure, it returns an error string
            print(atoms)
        else:
            # Then we execute the run method inside of its own instance
            for c, (runner, _) in enumerate(run_red_list):
                runs[c].append(runner(atoms, dict_list[c]))

    start_time = time.time()
    res = [ reduction([r.result() for r in runs[c]]) for c, (_, reduction) in enumerate(run_red_list) ]

    parsl.dfk().cleanup()

    return res