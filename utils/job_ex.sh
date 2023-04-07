#!/bin/bash
#SBATCH --job-name=xom_job
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=JobName-%j.out
#SBATCH --error=JobName-%j.err
#SBATCH --account=pi-lgrandi
#SBATCH --qos=xenon1t
#SBATCH --partition=xenon1t

CONTAINER_PATH="/project2/lgrandi/xenonnt/singularity-images/xenonnt-development.simg"
SCRIPT="/home/pellegriniq/xom_v1.py 031831"
USER=gaior
RUNDIR="/home/gaior/codes/xom/backend/algorithms/scada/"

echo $INNER_SCRIPT

module load singularity

singularity exec --bind /cvmfs/ --bind /project/ --bind /project2/ --bind /scratch/midway2/$USER --bind /dali $CONTAINER_PATH python3 $SCRIPT

