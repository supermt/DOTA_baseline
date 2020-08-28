import os
import pathlib
import subprocess
from shutil import copyfile, rmtree
import re
import copy
import psutil

import db_bench_option

from db_bench_option import *
# from db_bench_option import CPU_IN_TOTAL
# from db_bench_option import SUDO_PASSWD
# from db_bench_option import CPU_RESTRICTING_TYPE
from parameter_generator import HardwareEnvironment

CGROUP_NAME = "test_group1"


def turn_on_cpu(id):
    # command = "echo 1 | sudo tee /sys/devices/system/cpu/cpu1/online"
    os.system(
        "echo %s|sudo -S %s" % (SUDO_PASSWD, "echo 1 | sudo tee /sys/devices/system/cpu/cpu" + str(id) + "/online"))


def turn_off_cpu(id):
    # command = "echo 1 | sudo tee /sys/devices/system/cpu/cpu1/online"
    os.system(
        "echo %s|sudo -S %s" % (SUDO_PASSWD, "echo 0 | sudo tee /sys/devices/system/cpu/cpu" + str(id) + "/online"))


def restrict_cpus(count, type=0):
    if type == 0:
        restrict_cpus_by_cgroup(count)
    else:
        restrict_cpus_by_turning(count)


def restrict_cpus_by_cgroup(count):
    cgget_result = subprocess.run(
        ['cgget', '-g', 'cpu:'+CGROUP_NAME], stdout=subprocess.PIPE)
    result_strings = cgget_result.stdout.decode('utf-8').split("\n")
    cpu_period_time = 0
    for result_string in result_strings:
        if "cpu.cfs_period_us" in result_string:
            cpu_period_time = int(result_string.split(" ")[1])
    cpu_period_time = cpu_period_time
    print("CPU period time is %d ms" % cpu_period_time)
    cgset_result = subprocess.run(
        ['cgset', '-r', 'cpu.cfs_period_us='+str(cpu_period_time), CGROUP_NAME], stdout=subprocess.PIPE)

    cgset_result = subprocess.run(
        ['cgset', '-r', 'cpu.cfs_quota_us='+str(count*cpu_period_time), CGROUP_NAME], stdout=subprocess.PIPE)

    back_string = cgset_result.stdout.decode('utf-8')
    if back_string == "":
        print("Restrict the CPU period to "+str(count)+" times of CPU quota")
    else:
        print("Restrcting failed due to"+back_string)


def restrict_cpus_by_turning(count):
    reset_CPUs()
    count = int(count)
    if (count > CPU_IN_TOTAL):
        # too many cores asked
        print("no that many cpu cores", count)
        return
    else:
        print("restricting the CPU cores to ", count)
        for id in range(count, CPU_IN_TOTAL):
            turn_off_cpu(id)
        print("finished")


def reset_CPUs():
    if CPU_RESTRICTING_TYPE == 1:
        for id in range(1, CPU_IN_TOTAL):
            turn_on_cpu(id)
    else:
        subprocess.run(
            ['cgset', '-r', 'cpu.cfs_quota_us=-1', CGROUP_NAME])
    print("Reset all cpus")


def create_db_path(db_path):
    try:
        pathlib.Path(db_path).mkdir(parents=True, exist_ok=False)
    except Exception:
        print("Path Exists, clearing the files")
        rmtree(db_path)
        pathlib.Path(db_path).mkdir(parents=True, exist_ok=False)


def initial_cgroup():
    cgcreate_result = subprocess.run(
        ['cgcreate', '-g', 'blkio,cpu:/'+CGROUP_NAME], stdout=subprocess.PIPE)
    if cgcreate_result.stdout.decode('utf-8') != "":
        raise Exception("Cgreate failed due to:" +
                        cgcreate_result.stdout.decode('utf-8'))


def clean_cgroup():
    cgdelete_result = subprocess.run(
        ['cgdelete', '-r', 'blkio,cpu:/'+CGROUP_NAME], stdout=subprocess.PIPE)
    if cgdelete_result.stdout.decode('utf-8') != "":
        raise Exception("Cgreate failed due to:" +
                        cgdelete_result.stdout.decode('utf-8'))


def start_db_bench(db_bench_exec, db_path, options={}, cgroup={}, perf={}):
    """
    Starting the db_bench thread by subprocess.popen(), return the Popen object
    ./db_bench --benchmarks="fillrandom" --key_size=16 --value_size=1024 --db="/media/supermt/hdd/rocksdb"
    """
    if not cgroup:
        cgroup = {"cgexec": "/usr/bin/cgexec",
                  "argument": "-g",
                  "groups": "blkio,cpu:"+CGROUP_NAME
                  }
    # print(options["db"])
    db_path = os.path.abspath(db_path)
    options["db"] = db_path
    create_target_dir(db_path)
    with open(db_path + "/stdout.txt", "wb") as out, open(db_path + "/stderr.txt", "wb") as err:
        print("DB_BENCH starting, with parameters:")
        db_bench_options = parameter_tuning(
            os.path.abspath(db_bench_exec), para_dic=options)
        bootstrap_list = []

        if cgroup:
            # cgroup = {"cgexec":"/usr/bin/cgexec","argument","-g","groups","blkio,cpu:a_group"}
            bootstrap_list.extend(cgroup.values())

        bootstrap_list.extend(db_bench_options)

        db_bench_process = subprocess.Popen(
            bootstrap_list, stdout=out, stderr=err)

        #db_bench_process = subprocess.Popen(db_bench_options, stdout=out, stderr=err)
        print(parameter_printer(db_bench_options))
        # in case there are too many opened files
        os.system('echo %s|sudo -S %s' % (SUDO_PASSWD, "prlimit --pid " +
                                          str(db_bench_process.pid) + " --nofile=20480:40960"))

    print(db_bench_process.pid)
    return db_bench_process


def copy_current_data(src_dir, dst_dir, timestamp, file_names=["MEMORY_USAGE0"]):
    if src_dir[-1] != '/':
        src_dir = src_dir + "/"
    if dst_dir[-1] != '/':
        dst_dir = dst_dir + "/"
    for file_name in file_names:
        print("Copying", file_name)
        copyfile(src_dir + file_name, dst_dir +
                 file_name + "_" + str(timestamp))
    return


def create_target_dir(target_path):
    # try:
    pathlib.Path(target_path).mkdir(parents=True, exist_ok=True)
    if len(os.listdir(target_path)) != 0:
        return True
    else:
        return False
    # except:
    #     print("Path Exists, clearing the files")
    #     rmtree(target_path)
    #     pathlib.Path(target_path).mkdir(parents=True, exist_ok=False)

class DB_TASK:
    db_bench = ""
    result_dir = ""
    parameter_list = {}
    cpu_cores = 1

    def __init__(self, para_list, db_bench, result_dir, cpu_cores):
        self.parameter_list = copy.deepcopy(para_list)
        self.db_bench = copy.deepcopy(db_bench)
        self.result_dir = copy.deepcopy(result_dir)
        self.cpu_cores = copy.deepcopy(cpu_cores)

    def run(self, gap=1):
        restrict_cpus(self.cpu_cores, CPU_RESTRICTING_TYPE)
        self.parameter_list["max_background_compactions"] = self.cpu_cores
        devices=["sda","sdb","nvme0n1"]
        db_paths = []
        # system_util_file = open("%s/util_file.csv"%self.result_dir,"w")
        # system_util_file.write("cpu,memory,path1,path2")

        if "db_path" in self.parameter_list:
            print("db_paths: %s" % self.parameter_list["db_path"])
            regex = r"(\.\/\w+)*(\/\w+)+"
            matches = re.finditer(
                regex, self.parameter_list["db_path"], re.MULTILINE)
            for m in matches:
                db_paths.append("%s/" % m.group(0))
            for db_path in db_paths:
                os.system("rm -f %s*" % db_path)

        try:
            timer = 0
            db_bench_process = start_db_bench(
                self.db_bench, self.parameter_list["db"], self.parameter_list)
            stat_recorder=open(self.parameter_list["db"]+"/stat_result.csv","w")

            print("Mission started, output is in:%s" % self.result_dir)
            # create_target_dir(self.result_dir)
            while True:
                try:
                    db_bench_process.wait(gap)
                    print("mission complete")
                    copy_current_data(self.parameter_list["db"], self.result_dir, timer,
                                      ["stderr.txt", "stdout.txt", "LOG","stat_result.csv"])
                    break
                except subprocess.TimeoutExpired:
                    timer = timer + gap
                    # time, dbpath1,size,dbpath2,size, cpu_util,device1,iostat1...
                    result_line=[timer]
                    for db_path in db_paths:
                        du_line = os.popen("du -s %s" % db_path).read()
                        du_result = du_line.split()[0]
                        if not du_result.isnumeric():
                            continue
                        result_line.append({db_path:int(du_result)})
                    top_lines = os.popen("top -d %d -b -n 1 -p %d" %
                                         (gap, db_bench_process.pid)).read().splitlines()
                    cpu_util = float(top_lines[-1].split()[-4])
                    result_line.append(cpu_util)
                    io_counter_dict = psutil.disk_io_counters(perdisk=True)
                    for device in devices:
                        result_line.append({device:
                        [io_counter_dict[device].read_bytes,
                        io_counter_dict[device].write_bytes]})
                    result_line = str(result_line)[1:-1]
                    stat_recorder.write(result_line+"\n")
                    pass
        except Exception as e:
            p = psutil.Process(db_bench_process.pid)
            print("stopping db_bench: " + str(db_bench_process.pid))
            print(str(e))
            copy_current_data(self.parameter_list["db"], self.result_dir, timer,
                                ["stderr.txt", "stdout.txt", "LOG","/stat_result.csv"])
            p.terminate()  # or p.kill()
            # clean the directory
            # create_target_dir(self.result_dir)
            # restore all cpus
            reset_CPUs()

        # reset_CPUs()
        return


class DB_launcher:
    db_bench_tasks = []
    db_bench = ""
    options = {}

    def __init__(self, env: HardwareEnvironment, result_base, db_bench=DEFAULT_DB_BENCH, extend_options={}):
        self.db_bench_tasks = []
        self.db_bench = db_bench
        self.options = copy.deepcopy(extend_options)
        self.prepare_directories(env, result_base)
        initial_cgroup()
        return

    def prepare_directories(self, env: HardwareEnvironment, work_dir="./db", db_bench=DEFAULT_DB_BENCH):
        work_dir = os.path.abspath(work_dir)
        # do not clean this directory
        pathlib.Path(work_dir).mkdir(parents=True, exist_ok=True)

        # check all parameters, prepare the directories and init the tasks

        sub_path = work_dir + "/"

        temp_para_dict = {}

        for material in env.path_list:
            material_dir = sub_path + str(material[1])
            pathlib.Path(material_dir).mkdir(parents=True, exist_ok=True)
            temp_para_dict["db"] = str(material[0])
            for cpu_count in env.get_current_CPU_experiment_set():
                result_dir = material_dir + "/" + str(cpu_count) + "CPU"
                temp_para_dict["max_background_compactions"] = str(cpu_count)
                for memory_budget in env.get_current_memory_experiment_set():
                    temp_para_dict["write_buffer_size"] = memory_budget
                    target_dir = result_dir + "/" + \
                        str(int(memory_budget / 1024 / 1024)) + "MB"
                    if create_target_dir(target_dir):
                        print("existing files in %s" % target_dir)
                    else:
                        temp_para_dict.update(self.options)
                        job = DB_TASK(temp_para_dict,
                                      DEFAULT_DB_BENCH, target_dir, cpu_count)
                        self.db_bench_tasks.append(job)
        return

    def run(self):

        for task in self.db_bench_tasks:
            task.run()
            # print(self.options)
            # pass
