running_time=2000
for media in nvme pm ssd hdd
do
    echo "In: $media, run for $running_time, clear the cache"
    sync; echo 1 > /proc/sys/vm/drop_caches
# Collect On CPU Results for all media
#   perf record -a -g -F 99 -o oncpu_perf_$media.data -- /home/supermt/git/DOTA_Rocksdb/db_bench --db=/home/supermt/rocksdb_$media --benchmarks=fillrandom,stats --num=483183820 --key_size=8 --value_size=100 --write_buffer_size=67108864 --target_file_size_base=67108864 --min_write_buffer_number_to_merge=1 --max_write_buffer_number=2 --level0_file_num_compaction_trigger=4 --max_background_compactions=12 --max_background_flushes=1 --threads=1 --bloom_bits=10 --compression_type=none --base_background_compactions=1 --report_bg_io_stats=False --subcompactions=1 --detailed_running_stats=True --report_interval_seconds=1 --mutable_compaction_thread_prior=false --statistics=true --duration=$running_time --report_file=/home/supermt/rocksdb_$media/report.csv --max_background_jobs=13 > $media.stdout

# Collect Off CPU Results for all media
#    sync; echo 1 > /proc/sys/vm/drop_caches
#    perf record -a -g -e sched:sched_stat_sleep -e sched:sched_switch -e sched:sched_process_exit -o offcpu_perf_$media.data -- /home/supermt/git/DOTA_Rocksdb/db_bench --db=/home/supermt/rocksdb_$media --benchmarks=fillrandom,stats --num=483183820 --key_size=8 --value_size=100 --write_buffer_size=67108864 --target_file_size_base=67108864 --min_write_buffer_number_to_merge=1 --max_write_buffer_number=2 --level0_file_num_compaction_trigger=4 --max_background_compactions=12 --max_background_flushes=1 --threads=1 --bloom_bits=10 --compression_type=none --base_background_compactions=1 --report_bg_io_stats=False --subcompactions=1 --detailed_running_stats=True --report_interval_seconds=1 --mutable_compaction_thread_prior=false --statistics=true --duration=$running_time --report_file=/home/supermt/rocksdb_$media/report.csv --max_background_jobs=13 > $media.stdout

# use the tool offcputime-bpfcc to analyze the problem 
    sync; echo 1 > /proc/sys/vm/drop_caches
    nohup /home/supermt/git/DOTA_Rocksdb/db_bench --db=/home/supermt/rocksdb_$media --benchmarks=fillrandom,stats --num=483183820 --key_size=8 --value_size=100 --write_buffer_size=67108864 --target_file_size_base=67108864 --min_write_buffer_number_to_merge=1 --max_write_buffer_number=2 --level0_file_num_compaction_trigger=4 --max_background_compactions=12 --max_background_flushes=1 --threads=1 --bloom_bits=10 --compression_type=none --base_background_compactions=1 --report_bg_io_stats=False --subcompactions=1 --detailed_running_stats=True --report_interval_seconds=1 --mutable_compaction_thread_prior=false --statistics=true --duration=$running_time --report_file=/home/supermt/rocksdb_$media/report.csv --max_background_jobs=13 > $media.stdout &
    offcputime-bpfcc --stack-storage-size=2048 -df -p `pgrep -nx db_bench` $running_time > offline_$media.out.stacks
    sleep 5
    mv /home/supermt/rocksdb_$media/report.csv ./db_bench_results/report_$media.csv
    mv $media.stdout ./db_bench_results/
    mv perf_$media.data ./perf_results/
    mv offline_$media.out.stacks ./perf_results/

done

