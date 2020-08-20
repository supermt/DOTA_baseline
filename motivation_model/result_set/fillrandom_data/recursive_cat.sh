for f in `find .`; 
    do cat "$f" | grep MB/s
done

