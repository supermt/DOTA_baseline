import sys
import os

work_path = os.getcwd()
os.chdir("../")
sys.path.insert(0, '.')

import json
from db_bench_runner import clean_cgroup
from parameter_generator import StorageMaterial
from parameter_generator import HardwareEnvironment
from db_bench_runner import reset_CPUs
from db_bench_runner import DB_launcher
from collections import namedtuple
import db_bench_option
from db_bench_option import set_parameters_to_env
from db_bench_option import load_config_file
from db_bench_option import DEFAULT_VALUE_SIZE
from db_bench_option import DEFAULT_DB_BENCH

os.chdir(work_path)


class db_path_generator:
    media_type_map = {}
    media1_size = []

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def generate_path_dict(self):
        # {"/path/to/result",10G},{}
        db_path_lists = []
        db_path_key_list = []
        media2_size = "200GB"
        media1_path = list(self.media_type_map.keys())[0]
        for media1_size in self.media1_size:
            # for media1_path in self.media_type_map:
            for media2_path in self.media_type_map:
                if media1_path == media2_path:
                    continue
                else:
                    db_path_key_list.append("%s_%s&%s_%s" %
                                            (media1_size, self.media_type_map[media1_path],
                                                "200GB", self.media_type_map[media2_path]))
                    # db_path_lists.append(
                    #     "{%s,%s},{%s,%s}" % (
                    #     media1_path, media1_size, media2_path, "200GB"))
                    db_path_lists.append(
                        [
                            {"path": media1_path, "size": media1_size},
                            {"path": media2_path, "size": media2_size}
                        ]
                    )
        return db_path_lists
        # pass


if __name__ == '__main__':
    env = HardwareEnvironment()

    parameter_dict = load_config_file('write_amplification.json')

    set_parameters_to_env(parameter_dict, env)

    result_dir_prefix = "/home/jinghuan/hetero_wa_test/"

    gen = db_path_generator(**parameter_dict['db_path_gen'])

    db_path_dict = gen.generate_path_dict()

    size_map = {"10G": "10737418240", "40G": "48318382080","80G":"85899345920"}
    compaction_style_map = {0: "level", 1: "universal"}

    for compaction_style in parameter_dict['io_option']["compaction_style"]:
        for db_size in parameter_dict['db_size']:
            num = int(int(size_map[db_size])/int(DEFAULT_VALUE_SIZE))
            for db_path_set in db_path_dict:
                result_dir = "%s%s/%s/" % (result_dir_prefix,
                                                compaction_style_map[compaction_style], "workload" + db_size)
                db_path_string = "{"
                for db_path in db_path_set:
                    result_dir += db_path['size'] + "_" + \
                        gen.media_type_map[db_path['path']] + "&"
                    db_path_string += (db_path['path'] +
                                        ","+db_path['size'])
                    db_path_string += "},{"
                result_dir = result_dir[:-1]
                print(result_dir)
                db_path_string = db_path_string[:-2]
                env.set_storage_path(
                    db_path_set[0]['path'], StorageMaterial.HYBRID)
                extend_options = {"db_path": db_path_string}
                extend_options.update(
                    {"compaction_style": compaction_style})
                extend_options.update({"num":num})
                # print(extend_options)
                runner = DB_launcher(
                    env, result_dir, db_bench=DEFAULT_DB_BENCH, extend_options=extend_options)
                runner.run()
                reset_CPUs()
            clean_cgroup()
