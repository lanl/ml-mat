# Configuration for the darwin cluster
# This research used resources provided by the Darwin testbed at Los Alamos National Laboratory (LANL) which is funded by the Computational Systems and Software Environments subprogram of LANL's Advanced Simulation and Computing program (NNSA/DOE).
from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.providers import SlurmProvider

configs = {
    "darwin": Config(
        executors = [
            HighThroughputExecutor(
                label = "gpu-executor",
                worker_debug = False,
                max_workers_per_node=40,
                cores_per_worker = 1,
                cpu_affinity='alternating',
                provider = SlurmProvider(
                    partition = "skylake-gold",
                    nodes_per_block = 5,
                    init_blocks = 1,
                    max_blocks = 1,
                    cmd_timeout = 60,
                    walltime = '00:25:00',
                    launcher = SrunLauncher(),
                    worker_init = 'echo "Got node $(hostname)" && echo $(pwd) && module load miniconda3 cuda && conda init && conda activate mat-env-shared-gpu'
                )
            )
        ]
)
}