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

def execute_runner(config, runner, reduction, files, *args):  
    parsl.load(config)

    r = Base(files)
    print("Executing runner...")

    # We want to parse the CIF files in parallel...
    runs = []
    for atoms, success in r.open_file():
        if not success:
            # In the case of failure, it returns an error string
            print(atoms)
        else:
            # Then we execute the run method inside of its own instance
            runs.append(runner(atoms, args))

    start_time = time.time()
    res = [r.result() for r in runs]
    print("--- Execution took %s seconds ---" % (time.time() - start_time))   

    parsl.dfk().cleanup()

    return reduction(res)