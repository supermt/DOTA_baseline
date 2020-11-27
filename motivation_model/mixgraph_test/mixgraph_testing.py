# default path parameter
import os
import sys

work_path = os.getcwd()
os.chdir("../")
print(os.getcwd())
sys.path.insert(0, '.')

from db_bench_runner import clean_cgroup
from parameter_generator import StorageMaterial
from parameter_generator import HardwareEnvironment
from db_bench_runner import reset_CPUs
from db_bench_runner import DB_launcher
from db_bench_option import set_parameters_to_env
from db_bench_option import load_config_file
from db_bench_option import DEFAULT_DB_BENCH



os.chdir(work_path)
if __name__ == '__main__':
    env = HardwareEnvironment()
    parameter_dict = load_config_file('mixgraph.json')
    set_parameters_to_env(parameter_dict, env)

    result_dir_prefix = "/home/supermt/mixgraph_90_keyrange"

    # generate the keyrange of rows
    Key_distribution_config = {
        "keyrange_dist_a": 15.18,
        "keyrange_dist_b": -2.917,
        "keyrange_dist_c": 0.0164,
        "keyrange_dist_d": -0.08082,
        "keyrange_num": 90
    }

    # value_size distribution
    value_size_config = {
        "value_k": 0.2615,
        "value_sigma": 25.45
    }

    iter_config = {
        "iter_k": 2.517,
        "iter_sigma": 14.236
    }

    # operation
    operation_ratio_config = {
        # "mix_get_ratio": 0.5,
        "mix_put_ratio": 1,
        "mix_seek_ratio": 0.0
    }

    # ratio distribution
    qps_config = {
        "sine_mix_rate_interval_milliseconds": 5000,
        "sine_a": 1000,
        "sine_b": 0.0073,
        "sine_d": 450000
    }

    shared_config = {"benchmarks": "mixgraph",
                    "num": 500000000, "report_interval_seconds": 1,
                     "perf_level": 2,
                     "key_size": 48}

    result_dir = result_dir_prefix
    print(result_dir)
    extend_option_map = {}
    extend_option_map.update(Key_distribution_config)
    # extend_option_map.update(value_size_config)
    extend_option_map.update(iter_config)
    extend_option_map.update(operation_ratio_config)
    extend_option_map.update(qps_config)
    extend_option_map.update(shared_config)

    print(env)

    runner = DB_launcher(
        env, result_dir, db_bench=DEFAULT_DB_BENCH, extend_options=extend_option_map)
    runner.run()
    reset_CPUs()
    clean_cgroup()
