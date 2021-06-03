for cpu_num in 1 4 8
do
cd $cpu_num/
for media in nvme pm ssd hdd
    do 
	perf script -i perf_results/oncpu_perf_$media.data | /home/supermt/git/FlameGraph/stackcollapse-perf.pl > $media.out.perf-folded
	/home/supermt/git/FlameGraph/flamegraph.pl $media.out.perf-folded > perf-kernel-count-$media.svg
	/home/supermt/git/FlameGraph/flamegraph.pl --color=chain --title="Off-CPU Time Flame Graph $cpu_num thread(s) $media" --countname=us < perf_results/offline_$media.out.stacks > offcpu-perf-$media.svg
    done
chmod 666 *.svg
cd ../
done
