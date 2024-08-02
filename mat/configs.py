# Configuration for the darwin cluster
# This research used resources provided by the Darwin testbed at Los Alamos National Laboratory (LANL) which is funded by the Computational Systems and Software Environments subprogram of LANL's Advanced Simulation and Computing program (NNSA/DOE).
from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.providers import SlurmProvider, LocalProvider

def get_local(max_blocks, parallelism):
    return Config(
        executors = [HighThroughputExecutor(
            label = "local-executor",
            worker_debug = False,
            max_workers_per_node=40,
            cores_per_worker = 0.01,
            provider = LocalProvider(
                max_blocks = max_blocks,
                parallelism = parallelism,
                worker_init = "module load miniconda3 && conda init && conda activate mat-env"
            )
        )]
    )

configs = {
    "darwin": Config(
        executors = [
            HighThroughputExecutor(
                label = "gpu-executor",
                max_workers=700,
                max_workers_per_node=44,
                cores_per_worker=1,
                cpu_affinity='alternating',
                provider = SlurmProvider(
                    partition = "skylake-gold",
                    nodes_per_block = 4,
                    init_blocks = 1,
                    max_blocks = 3,
                    cmd_timeout = 60,
                    walltime = '08:00:00',
                    launcher = SrunLauncher(overrides='-c 64'),
                    worker_init = 'echo "Got node $(hostname)" && echo $(pwd) && module load miniconda3 && conda init && conda activate mat-env'
                )
            )
        ]
    ),
    "local": get_local(1, 0.95)
}
