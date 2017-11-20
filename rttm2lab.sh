#!/bin/bash
#
# author=Julien Karadyai
#
# convert rttm file to lab

# Parameters
if (( $# != 2 )); then
    echo "Usage: $0 <rttm_dir> <output_dir>"
    exit 1
fi

rttm_folder=$(readlink -f $1)
output_folder=$(readlink -f $2)

if [ ! -d $output_folder ]; then
    mkdir -p $output_folder
fi

for fin in `ls $rttm_folder`; do
    lab_name=`echo $fin | cut -d '.' -f 1 | awk '{print $0".lab"}'`
    awk '{if ($8=="speech") {print $4" "($4+$5)" "$8}}' $rttm_folder/$fin > $output_folder/$lab_name 
done
