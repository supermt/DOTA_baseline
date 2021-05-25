running_time=2000
for cpu_num in 1 4 8
do
	for media in nvme pm ssd hdd
	do
	    echo "In: $media, run for $running_time, clear the cache"
	# Collect On CPU Results for all medi	# use the tool offcputime-bpfcc to analyze the problem 
	    sync; echo 1 > /proc/sys/vm/drop_caches
	    nohup /home/supermt/git/DOTA_Rocksdb/db_bench --db=/home/supermt/rocksdb_$media --benchmarks=fillrandom,stats --num=483183820 --key_size=8 --value_size=100 --write_buffer_size=67108864 --target_file_size_base=67108864 --min_write_buffer_number_to_merge=1 --max_write_buffer_number=2 --level0_file_num_compaction_trigger=4 --max_background_compactions=$cpu_num --max_background_flushes=1 --threads=1 --bloom_bits=10 --compression_type=none --base_background_compactions=1 --report_bg_io_stats=False --subcompactions=1 --detailed_running_stats=True --report_interval_seconds=1 --mutable_compaction_thread_prior=false --statistics=true --duration=$running_time --report_file=/home/supermt/rocksdb_$media/report.csv > $media.stdout 2>$media.stderr &
	    nohup perf record -a -g -F 99 -o oncpu_perf_$media.data -p `pgrep -nx db_bench` > perf_command.log 2>perf_command.err &
	    offcputime-bpfcc --stack-storage-size=2048 -df -p `pgrep -nx db_bench` $running_time > offline_$media.out.stacks 
            sleep 5
	    mkdir -p $cpu_num/db_bench_results
	    mkdir -p $cpu_num/perf_results
	    cd $cpu_num
	    mv /home/supermt/rocksdb_$media/report.csv ./db_bench_results/report_$media.csv
	    mv ../$media.stdout ./db_bench_results/
	    mv ../oncpu_perf_$media.data ./perf_results/
	    mv ../offline_$media.out.stacks ./perf_results/
            cd ../
	done
done 
