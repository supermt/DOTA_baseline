# default path parameter

from db_bench_option import DEFAULT_DB_BENCH
from db_bench_option import load_config_file
from db_bench_option import set_parameters_to_env

from db_bench_runner import DB_launcher
from db_bench_runner import reset_CPUs
from parameter_generator import HardwareEnvironment
from db_bench_runner import clean_cgroup
from configparser import ConfigParser
import json

if __name__ == '__main__':
    env = HardwareEnvironment()
    set_parameters_to_env(load_config_file(),env)
    
    runner = DB_launcher(env,"/home/jinghuan/basic_results", db_bench=DEFAULT_DB_BENCH)

    runner.run()
    reset_CPUs()
    clean_cgroup()
