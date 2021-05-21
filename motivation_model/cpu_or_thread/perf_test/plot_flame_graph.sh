for media in nvme pm ssd hdd
do
 
    perf script -i perf_results/oncpu_perf_$media.data | grep rocksdb | /home/supermt/git/FlameGraph/stackcollapse-perf.pl > $media.out.perf-folded
    /home/supermt/git/FlameGraph/flamegraph.pl $media.out.perf-folded > perf-kernel-$media.svg
    /home/supermt/git/FlameGraph/flamegraph.pl --color=io --title="Off-CPU Time Flame Graph" --countname=us < perf_results/offline_$media.out.stacks > offcpu-perf-$media.svg
done
