perf script -i perf.data | /home/supermt/git/FlameGraph/stackcollapse-perf.pl > out.perf-folded
/home/supermt/git/FlameGraph/flamegraph.pl out.perf-folded > perf-kernel-nvme.svg

