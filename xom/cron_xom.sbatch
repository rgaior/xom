#!/bin/bash

#SBATCH --time=00:05:00
#SBATCH --output=cron.log
#SBATCH --open-mode=append
#SBATCH --account=cron-account
#SBATCH --partition=cron
#SBATCH --qos=cron

# Specify a valid Cron string for the schedule. This specifies that
# the Cron job run once per day at 5:15a.
SCHEDULE='* * * * *'

# Here is an example of a simple command that prints the host name and
# the date and time.

echo "Cron Job at $(date)." >> test_cron.txt

# This schedules the next run.
sbatch --quiet --constraint=edr --begin=$(next-cron-time "$SCHEDULE") cron_xom.sbatch
/bin/bash /project2/lgrandi/xenonnt/development/xnt_env
/bin/bash /home/mlotfi/xom/xom/backend/run_xom_simu_db.sh
