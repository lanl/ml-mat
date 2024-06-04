from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.providers import SlurmProvider

def getConfig():
    return Config(
        executors = [
            HighThroughputExecutor(
                label = "test",
                worker_debug = False,
                cores_per_worker = 2,
                cpu_affinity='alternating',
                provider = SlurmProvider(
                    partition = "shared-gpu",
                    nodes_per_block = 2,
                    init_blocks = 1,
                    max_blocks = 1,
                    cmd_timeout = 60,
                    walltime = '00:10:00',
                    launcher = SrunLauncher(),
                    worker_init = 'source ~/test-env/bin/activate'
                )
            )
        ]
    )