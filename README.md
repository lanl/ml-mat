# ML Mat

## CI Example
So, here is an example of running simple `unittests`, some of which have to do with Parsl directly (the `config.py` and `mcarlo.py` files). The virtual environment is in my current home directory, but a shared folder is better.

### Note
Currently, the shell script just assumes that the correct environment is inside the `~/` directory. However, we should obtain a [shared directory](https://darwin.lanl.gov/doku.php?id=faq:sharedproject) that all of the CI runners can grab their environment from. Also, we should [have different environments for each node type](https://darwin.lanl.gov/doku.php?id=tutorial:pythonexample&s[]=python#:~:text=Darwin%20is%20a,were%20built%20for.) if we want to execute across different archs. 