# ./db_bench --db_path='[{"/home/jinghuan/rocksdb_nvme/", 10GB},{"/home/jighuan/rocksdb_hdd/", 1TB}]'

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

    parameter_dict = load_config_file('hybrid_test_ssd.json')
    set_parameters_to_env(parameter_dict, env)

    result_dir_prefix = "/home/jinghuan/hetero"

    db_path_options = parameter_dict["db_path"]

    # print(len(db_path_options))
    # for db_path_unit in db_path_options:
    #     db_path_string = "{"
    #     for db_path in db_path_unit:
    #         db_path_string += (db_path['path'] + ","+db_path['size'])
    #         db_path_string += "},{"
    #     db_path_string = db_path_string[:-2]

    for db_path_set in db_path_options:
        result_dir = result_dir_prefix + "/"
        db_path_string = "{"
        for db_path in db_path_set:
            result_dir  += db_path['size'] + "_" +db_path['media'] + "&"
            db_path_string += (db_path['path'] + ","+db_path['size'])
            db_path_string += "},{"
        result_dir = result_dir[:-1]
        db_path_string = db_path_string[:-2]
        env.set_storage_path(db_path_set[0]['path'],StorageMaterial.HYBRID)
        extend_options = {"db_path": db_path_string}
        runner = DB_launcher(
            env, result_dir, db_bench=DEFAULT_DB_BENCH, extend_options=extend_options)
        runner.run()
        reset_CPUs()
    # runner.run()
    # reset_CPUs()
    clean_cgroup()
