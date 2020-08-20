# default path parameter

from db_bench_option import DEFAULT_DB_BENCH
from db_bench_option import load_config_file
from db_bench_option import set_parameters_to_env

from db_bench_runner import DB_launcher
from db_bench_runner import reset_CPUs
from parameter_generator import HardwareEnvironment
from parameter_generator import StorageMaterial
from motivation_bootstrap import set_parameters_to_env

from db_bench_runner import clean_cgroup

if __name__ == '__main__':
    env = HardwareEnvironment()
    # env.config_CPU_by_list([12])
    # env.config_Memory(min_mem=(64 * 1024 * 1024), set_size=1)

    # env.add_storage_path("/home/jinghuan/rocksdb_nvme",StorageMaterial.NVMeSSD)
    # env.add_storage_path("/home/jinghuan/rocksdb_hdd",StorageMaterial.SATAHDD)
    # env.add_storage_path("/home/jinghuan/rocksdb_ssd",StorageMaterial.SATASSD)

    # reset_CPUs()
    # pdl["use_direct_io_for_flush_and_compaction"]=False
    # runner = DB_launcher(env,"/home/jinghuan/none_direct_io", db_bench=DEFAULT_DB_BENCH)
    # runner.run()

    # # set db_option here
    # pdl["use_direct_io_for_flush_and_compaction"]=True
    # runner = DB_launcher(env,"/home/jinghuan/with_direct_io", db_bench=DEFAULT_DB_BENCH)
    # runner.run()

    # reset_CPUs()
    parameter_dict = load_config_file('wal_path_sets.json')
    set_parameters_to_env(parameter_dict,env)

    result_dir_prefix = "/home/jinghuan/io_option_difference"


    io_options = parameter_dict["io_options"]

    for io_option_key in io_options:
        for io_option_value in io_options[io_option_key]:
            result_dir = result_dir_prefix + "/%s/%s" % (io_option_key, str(io_option_value))
            print(result_dir)
            extend_options = {io_option_key:io_option_value}
            runner = DB_launcher(env,result_dir, db_bench=DEFAULT_DB_BENCH,extend_options=extend_options)
            runner.run()
            reset_CPUs()
    # runner.run()
    # reset_CPUs()
    clean_cgroup()
