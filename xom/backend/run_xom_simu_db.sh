#!/bin/bash

file_name_db=run_numbers_simu_db.txt

while read run_info
do
    # get all the infos inside the file, line by line
    IFS=" " read -r  data_type data_source run_name run_number context_version <<<"$run_info"   
    if [ -z "$context_version" ]
    then
	context_version=v1.0
    fi
    echo "the run number is: $run_number"
	
    #assign the outputfolder
    outputfolder=/scratch/midway2/mlotfi/$context_version/$run_number
    # here we run the process manager
    ./processManager --dataType $data_type --source $data_source --runName $run_name --runId $run_number --outFolder $outputfolder

    rsync -avz   /scratch/midway2/mlotfi/$context_version  xom@xe1t-offlinemon.lngs.infn.it:/home/xom/data/xom
    #now we can delete the whole directory, but only if the rsync is succefull
    if [[ $? -gt 0 ]]
    then
    #send an email for failure of the rsync
	echo "The run number: $run_number failed to sync with context version $context_version" |  mail -s "fail syncing the run $run_number" mlb20@nyu.edu
	echo "There is problem syncing the run $run_number"
    else
	rm -rf /scratch/midway2/mlotfi/$context_version/
    fi
	
    # now lets sleep 5 minutes before we go for the next run
    sleep 300
    
done<$file_name_db

