import sys
import os

work_path = os.getcwd()
os.chdir("../")
sys.path.insert(0,'.')

from db_bench_option import DEFAULT_DB_BENCH
from db_bench_option import load_config_file
from db_bench_option import set_parameters_to_env
from collections import namedtuple

from db_bench_runner import DB_launcher
from db_bench_runner import reset_CPUs
from parameter_generator import HardwareEnvironment
from parameter_generator import StorageMaterial
from db_bench_option import set_parameters_to_env

from db_bench_runner import clean_cgroup
import json

os.chdir(work_path)


if __name__ == '__main__':
    env = HardwareEnvironment()

    parameter_dict = load_config_file('nvme_only.json')

    set_parameters_to_env(parameter_dict, env)

    result_dir_prefix = "/home/jinghuan/hetero_wa_test/"

    size_map = {"10G": "10737418240", "40G": "48318382080"}
    compaction_style_map = {0: "level", 1: "universal"}
    for compaction_style in parameter_dict['io_option']["compaction_style"]:
        for db_size in parameter_dict['db_size']:
            DEFAULT_DB_SIZE = size_map[db_size]
            result_dir = "%s%s/%s/%s" % (result_dir_prefix,
                                            compaction_style_map[compaction_style], "workload" + db_size,"NVMeSSD_Only")

            print(result_dir)
        #     db_path_string = db_path_string[:-2]
        #     env.set_storage_path(db_path_set[0]['path'], StorageMaterial.HYBRID)
            extend_options={"compaction_style":compaction_style}
        #     # print(extend_options)
            runner = DB_launcher(
                env, result_dir, db_bench=DEFAULT_DB_BENCH, extend_options=extend_options)
            runner.run()
            reset_CPUs()
        clean_cgroup()
