from parsl import python_app
from ase import Atoms, io
from typing import Union, List

class WrappedAtomsRunner:
    def __init__(self, file_location: Union[str, List[str]]):
        self.file_locations = [file_location] if isinstance(file_location, str) else file_location
        
    def open_file(self):
        for file_loc in self.file_locations:
            try:
                yield io.read(file_loc), True
            except Exception as e:
                yield "Error reading file: " + str(e), False

@python_app
def execute_single(atoms: Atoms, runner: WrappedAtomsRunner):
    try:
        return runner.run(atoms)
    except Exception as e:
        print("Error executing runner: ", str(e))
        return False

@python_app
def execute_runner(runner: WrappedAtomsRunner, reduction):
    # We want to parse the CIF files in parallel...
    runs = []
    for atoms, success in runner.open_file():
        if not success:
            # In the case of failure, it returns an error string
            print(atoms)
        else:
            # Then we execute the run method inside of its own instance
            runs.append(execute_single(atoms, runner))

    return reduction.reduce([r.result() for r in runs])