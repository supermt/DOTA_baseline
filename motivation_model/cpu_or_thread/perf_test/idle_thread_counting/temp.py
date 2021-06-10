import pandas as pd


def func_count_on_syscalls(fname="offline_ssd.out.stacks"):
    f = open(fname)
    lines = f.readlines()
    all_syscall = 0

    sys_call_list = ["sys_write",
                     "sys_futex",
                     "sys_fdatasync",
                     "sys_fsync",
                     "sys_fallocate",
                     "sys_unlink",
                     "sys_pread",
                     "exit_to_usermode_loop",
                     "sys_mmap",
                     "sys_munmap",
                     "sys_open",
                     "sys_newstat",
                     "sys_ftruncate"
                     ]

    wake_up_call_list = sys_call_list + \
        ["ret_from_intr", "mprotect"]

    sys_call_time_records_map = {x: [] for x in sys_call_list}
    wake_call_records_map = {x: [] for x in wake_up_call_list}
    overall_off_cpu_time = 0
    thread_resume = []
    blocked_loop_records = []
    io_queue_locked_records = []
    timer_interrupt_records = []
    waiting_for_jbd = []
    unkown_reason_blocked = []

    for line in lines:
        if "db_bench" in line or "rocksdb" in line:
            wake_chain = line.split("--")
            if (len(wake_chain) != 2) or line == "\n":
                print(wake_chain)
                continue

            sleep_time = line.split(" ")[-1]
            sleep_time = int(sleep_time)
            overall_off_cpu_time += sleep_time

            off_cpu_part = wake_chain[0]
            wake_up_part = wake_chain[1]
            if "do_syscall" in off_cpu_part:
                all_syscall += 1
                sys_call_matched = 0
                for action in sys_call_list:
                    if action in off_cpu_part:
                        sys_call_time_records_map[action].append(sleep_time)
                        sys_call_matched += 1
                if sys_call_matched != 1:
                    print("syscall multi matched", line, sys_call_matched)
                    pass
            # can't find the syscall in the sleeping part, search the waking part
            elif "do_syscall" in wake_up_part:
                sys_call_matched = 0
                for action in wake_up_call_list:
                    if action in wake_up_part:
                        wake_call_records_map[action].append(sleep_time)
                        sys_call_matched += 1
                if sys_call_matched != 1:
                    if "ret_from_intr" not in wake_up_part:
                        print(
                            "uncaptured syscalls, or syscalls with multiple actions", line, sys_call_matched)
                        pass
            elif "swapgs_restore_regs_and_return_to_usermode;prepare_exit_to_usermode;exit_to_usermode_loop;schedule;" in line:
                pure_wake_message = line.split("--")[1].split(" ")
                if pure_wake_message[0] == ";;":
                    thread_resume.append(int(pure_wake_message[1]))
                else:
                    # print("wake up entry with further dependencies", line)
                    thread_resume.append(sleep_time)
                    pass
            elif "swapper" in line:
                blocked_loop_records.append(sleep_time)
                # no syscalls, and it's not called from the wakeup loop
            elif "unlock_buffer" in line:
                io_queue_locked_records.append(sleep_time)
            elif "apic_timer_interrupt" in line:
                timer_interrupt_records.append(sleep_time)
            elif "jbd2" in line:
                waiting_for_jbd.append(sleep_time)
            elif "SyncInternal" in line:
                io_queue_locked_records.append(sleep_time)
            else:
                unkown_reason_blocked.append(sleep_time)
                # print(line)
                pass

    results_dict = {
        "thread_resume": thread_resume,
        "thread_blocked": blocked_loop_records,
        "io_queue_blocked": io_queue_locked_records,
        "time_IRQ_switch": timer_interrupt_records,
        "unkown": unkown_reason_blocked
    }
    return sys_call_time_records_map, wake_call_records_map, results_dict


def func_timing_statistic(syscall_map, waker_syscall_map, nosyscall_map, to_sec=True):
    present_dict = {
        "sys_futex": ["sys_futex"],
        "sys_io_blocking": ["sys_write", "sys_fdatasync", "sys_fsync", "sys_fallocate", "sys_pread", "sys_mmap", "sys_munmap", "sys_open", "sys_newstat", "sys_ftruncate"],
        "thread_switching": 0,
        "others": 0
    }

    metrics_counting_dict = {}
    metrics_time_dict = {}

    metrics_time_dict["sys_futex"] = sum(
        syscall_map["sys_futex"]) + sum(waker_syscall_map["sys_futex"])
    metrics_counting_dict["sys_futex"] = len(
        syscall_map["sys_futex"]) + len(waker_syscall_map["sys_futex"])

    sys_io_blocking_time = 0
    sys_io_hit_count = 0

    for key in present_dict["sys_io_blocking"]:
        sys_io_blocking_time += (sum(syscall_map[key]) +
                                 sum(waker_syscall_map[key]))
        sys_io_hit_count += (len(syscall_map[key]) +
                             len(waker_syscall_map[key]))

    metrics_time_dict["sys_io_blocking"] = sys_io_blocking_time
    metrics_counting_dict["sys_io_blocking"] = sys_io_hit_count

    metrics_time_dict["thread_switching"] = sum(
        waker_syscall_map["ret_from_intr"]) + sum(waker_syscall_map["mprotect"]) + sum(nosyscall_map["thread_resume"]) + sum(nosyscall_map["io_queue_blocked"]) + sum(nosyscall_map["time_IRQ_switch"])
    metrics_counting_dict["thread_switching"] = len(
        waker_syscall_map["ret_from_intr"]) + len(waker_syscall_map["mprotect"]) + len(nosyscall_map["thread_resume"]) + len(nosyscall_map["io_queue_blocked"]) + len(nosyscall_map["time_IRQ_switch"])

    metrics_time_dict["others"] = sum(nosyscall_map["unkown"])
    metrics_counting_dict["others"] = len(nosyscall_map["unkown"])

    if to_sec:
        for metrics_time in metrics_time_dict:
            metrics_time_dict[metrics_time] = metrics_time_dict[metrics_time] / 1000000

    return metrics_counting_dict, metrics_time_dict


if __name__ == "__main__":
    MEDIA_LIST = ['pm', "nvme", "ssd", "hdd"]
    CPU_LIST = [1, 4, 8]
    key_list = ["thread_num", "material", "syscall_type", "time", "count"]
    result_df = pd.DataFrame(columns=key_list)
    for cpu_num in CPU_LIST:
        for media in MEDIA_LIST:
            syscall_map, waker_syscall_map, nosyscall_map = func_count_on_syscalls(
                "%d/perf_results/offline_%s.out.stacks" % (cpu_num, media))
            count_dict, time_dict = func_timing_statistic(
                syscall_map, waker_syscall_map, nosyscall_map)

            print("Time distribution (sec) of %d, %s" % (cpu_num, media))
            print(time_dict)
            for key in time_dict:
                value_list = [cpu_num, media, key,
                              time_dict[key], count_dict[key]]
                result_df = result_df.append(
                    dict(zip(key_list, value_list)), ignore_index=True)
    result_df.to_csv("time_distribution_in_off-CPU.csv")
    # for syscall_action in syscall_map:
