for cpu_num in 1 4 8
do
    cd $cpu_num/
    tar -czvf perf_results.tar.gz perf_results
    git add perf_results.tar.gz
    git add *.svg
    git add *.perf-folded
    git add db_bench_results
    cd ../
done

