import subprocess
import time
import os.path

FIO_COMMAND = "fio"

# here are the parameters we need to consider in our experiment
# 1. block_size 4k, 16k, 64k, 128k
# 2. ioengine: libaio, psync(default)
# 3. numjobs: 2, 4, 8 , 12 (up to 12 CPUs)
# 4. iodepth:1,2,4,8,16,32,64,128
# 5. directIO or bufferedIO
#
# fixed parameters:
# 3. operation: write, randomwrite


def path_to_media(file_path):
    return file_path.split("/")[-2].split("_")[-1]


# op,iodepth,numjobs,ioengine,bs,media
def para_to_filename(para_list):
    result = ""
    for key in para_list:
        if key == "filename":
            result = path_to_media(para_list[key]) + "_" + result
        elif key not in ["name", "group_reporting", "runtime", "size"]:
            result = str(para_list[key]) + "_" + result
    return result


def para_to_string(para_list):
    result = ""
    for para in para_list:
        result += para + " "
    return result


def para_dict_to_list(para_dict):
    result = []
    for key in para_dict:
        if key not in ["group_reporting"]:
            result.append("-"+key+"="+str(para_dict[key]))
        else:
            result.append("-"+key)
    return result


def function_fio_runner(job_list):
    for job in job_list:
        result_name = para_to_filename(job)
        print(result_name)
        if os.path.isfile(result_name[:-1]+".txt"):
           print("file exists, skip the test")
           continue
        with open(result_name[:-1]+".txt", "w") as out:
            bootstrap_list = [FIO_COMMAND]
            bootstrap_list.extend(para_dict_to_list(job))
            out.write(para_to_string(bootstrap_list))
            subprocess.run(bootstrap_list, stdout=out)
            time.sleep(60)
    # return fio_process
# fio -filename="test.file" -direct=1 -iodepth 1 -rw=randwrite -ioengine=psync -bs=16k -size=10G -numjobs=1 -runtime=60 -group_reporting -group_reporting -name=rw_test
# fio -filename=/home/jinghuan/rocksdb_nvme/fiotest -block_size=16k -ioengine=libaio -numjobs=2 -iodepth=16 -direct=1 -rw=randwrite -name=baseline_scanning -group_reporting -runtime=60 -size=10G


def init_dict(dict_keys):
    result = {}
    for key in dict_keys:
        result[key] = ""
    return result


def generate_para_group(op_type):
    fixed_para = {
        "rw": str(op_type),
        "name": "baseline_scanning",
        "group_reporting": "",
        "runtime": 60,
        "size": "10G"
    }
    flexible_para = {
        "filename": ["/home/jinghuan/rocksdb_nvme/fiotest", "/home/jinghuan/rocksdb_hdd/fiotest", "/home/jinghuan/rocksdb_ssd/fiotest"],
        "bs": ["4k", "16k", "64k"],
        "ioengine": ["psync", "libaio"],
        "numjobs": [1,4,16],
        "iodepth": [1, 16, 32, 64, 256],
        # "direct": [0, 1]
    }
    # flexible_para = {
    #     "filename": ["/home/jinghuan/rocksdb_ssd/fiotest"],
    #     "bs": ["4k", "16k", "64k"],
    #     "ioengine": ["psync", "libaio"],
    #     "numjobs": [1],
    #     "iodepth": [1, 16, 32, 64, 256],
    #     # "direct": [0, 1]
    # }
    # flexible_para = {
    #     "filename": ["/home/jinghuan/rocksdb_nvme/fiotest"],
    #     "bs": ["4k", "16k"],
    #     "ioengine": ["psync", "libaio"],
    #     "numjobs": [1, 2],
    #     "iodepth": [1, 16],
    #     # "direct": [0, 1]
    # }

    para_dict_list = []

    for file_name in flexible_para["filename"]:
        for block_size in flexible_para["bs"]:
            for io_engine in flexible_para["ioengine"]:
                for numjobs in flexible_para["numjobs"]:
                    for iodepth in flexible_para["iodepth"]:
                        temp_para = {"filename": file_name, "bs": block_size, "ioengine": io_engine,
                                     "numjobs": numjobs, "iodepth": iodepth}
                        temp_para.update(fixed_para)
                        para_dict_list.append(temp_para)
    print(len(para_dict_list))
    return para_dict_list


if __name__ == "__main__":
    function_fio_runner(generate_para_group("write"))
    function_fio_runner(generate_para_group("randwrite"))
    pass
