# ML Mat

## Code Design
![diagram](docs/diagram.png)

In order to parallelize the various aspects of the process, we expect the three items outlined in blue to be performed/supplied to all parsl instances. Thus, every *different kind of process* can be implemented in its own function that gets passed to it an `ase.Atoms` object obtained from a `CIF` file. This is what `runner.WrappedAtomsRunner` does. You inherit from this class and implement an `def run(atoms: ase.Atoms)` function. Then instantiate your class, pass the file name, and pass your instance along to `runner.execute_runner`. This will spawn a parsl task, load in the given file, and call your `run` method with the `ase.Atoms` obtained from the file. Then if you want to add an `ase.Calculator` to it to use `MACE-mp` or `VASP` you can, it's all self-contained within the task.

Check `example_runner` for an example of how this works.

### For Many Files
The `runner.WrappedAtomsRunner` base class takes either a string or a list of strings. The `open_file()` method `yield`s the atoms object for each filename in the list. Then a new parsl task is launched for each call to `run`. This means each *type* of runner will have its own instance *and* each invididual execution of the runner. 

The results of a type of runner are aggregated into a list which is then passed to the `reduction`, which simply implements a `reduce` method that takes a list of objects and returns the reduction. For example, each type of runner will have its own pandas data frame where each row is an individual run. So, the runs produce rows and then the reduction turns the list of rows into a dataframe.

## CI Example
So, here is an example of running simple `unittests`, some of which have to do with Parsl directly (the `config.py` and `mcarlo.py` files). The virtual environment is in my current home directory, but a shared folder is better.

### Note
Currently, the shell script just assumes that the correct environment is inside the `~/` directory. However, we should obtain a [shared directory](https://darwin.lanl.gov/doku.php?id=faq:sharedproject) that all of the CI runners can grab their environment from. Also, we should [have different environments for each node type](https://darwin.lanl.gov/doku.php?id=tutorial:pythonexample&s[]=python#:~:text=Darwin%20is%20a,were%20built%20for.) if we want to execute across different archs. 