#!/bin/bash

run_date=$(date +%Y-%m-%d)
combine_path='/home/mhabeb/combine'

#pre-combine threat files collection
feed_curl() {
	cd $combine_path
	curl -q http://cybercrime-tracker.net/all.php -o cybercrime_tracker.txt 2>&1 | tee feeds_$run_date.log
	return 0;
}
#combine run
exec_combine() {
	python $combine_path/combine.py 2>&1 | tee -a feeds_$run_date.log
	return 1;
}

#result verification
verify_out() {
	if [ $(date -r $combine_path/harvest.csv +%F) == $run_date ]
		then
			echo "$(date) - ThreatIntelli feeds collection succeeded" 2>&1 | tee -a feeds_$run_date.log
			return 0;
	fi
}

#post-combine SQLexport
sql_export() {
	python export_mySQL.py 2>&1 | tee -a feeds_$run_date.log
}

main()	{
	feed_curl
	if [ feed_curl ]
		then
			exec_combine
	fi

	if [ exec_combine ]
		then
			verify_out
	fi
	if [ verify_out ]
		then
			sql_export; echo "$(date) Threat Intelli feeds Database upload completed" 2>&1 | tee -a feeds_$run_date.log
			return 0;
	fi
}
main
