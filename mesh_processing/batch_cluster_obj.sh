display_usage() { 
	echo "This script is used to generate rotated versions of a set of objects." 
	echo -e "\nUsage:\n$0 [path to .obj folder] [path to vcglib executable] [grid size]\n" 
	} 

# if less than two arguments supplied, display usage 
	if [  $# -le 2 ] 
	then 
		display_usage
		exit 1
	fi 
 
# check whether user had supplied -h or --help . If yes display usage 
	if [[ ( $# == "--help") ||  $# == "-h" ]] 
	then 
		display_usage
		exit 0
	fi 

file_list=$(find $1 -name '*.obj' ! -name '*.sample.obj')
prog_path=$2
size=$3
len=$(echo $file_list | tr -cd ' ' | wc -c)
len=$((len+1))
echo "total file count: " $len
cnt=0

for f in $file_list
# for (( cnt=1; cnt<$len+1; cnt++ ));
do
	echo $f
	parentdir=$(dirname $f)

	cmd="$prog_path $f ${f/.obj/.cluster.obj} -s $size"
	eval '$cmd'

	cnt=$((cnt+1))
	echo "finished " $cnt " / " $len
done
