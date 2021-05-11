for media in nvme pm ssd hdd
do
 
    perf script -i perf_results/oncpu_perf_$media.data | /home/supermt/git/FlameGraph/stackcollapse-perf.pl > $media.out.perf-folded
    /home/supermt/git/FlameGraph/flamegraph.pl $media.out.perf-folded > perf-kernel-$media.svg

done
