
for media in nvme pm hdd ssd
do
    perf inject -v -s -i offcpu_perf_$media.data -o offcpu_perf_$media.data-folded
    perf script -F comm,pid,tid,cpu,time,period,event,ip,sym,dso,trace -i offcpu_perf_$media.data-folded| awk '
        NF > 4 { exec = $1; period_ms = int($5 / 1000000) }
        NF > 1 && NF <= 4 && period_ms > 0 { print $2 }
        NF < 2 && period_ms > 0 { printf "%s\n%d\n\n", exec, period_ms }' | \
        /opt/FlameGraph/stackcollapse.pl | \
        /opt/FlameGraph/flamegraph.pl --countname=ms --title="Off-CPU Time Flame Graph" --colors=io > offcpu_$media.svg
done
