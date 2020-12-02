needed_arguments=0
echo $1
if [ "$#" -le "$needed_arguments" ];
then
  echo "No enough arguments, missing workdir at $needed_arguments , received only $@"
else
  echo "Store the python log at $1"
  nohup python3 mixgraph_testing.py > /home/supermt/mixgraph_test/python.log 2>&1 &
  cp /home/supermt/mixgraph_test/python.log $1
fi


