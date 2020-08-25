#!/bin/bash -l

#SBATCH --job-name={job_name}
#SBATCH --time={time}
#SBATCH --nodes=1

# TODO parametrize
SCRATCH_DIR=/tmp/cpacpy-$SLURM_JOBID

mkdir -p $SCRATCH_DIR

# TODO parametrize installation
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O $SCRATCH_DIR/miniconda.sh
bash $SCRATCH_DIR/miniconda.sh -b -fp $SCRATCH_DIR/miniconda/
source $SCRATCH_DIR/miniconda/bin/activate

pip install git+https://github.com/radiome-lab/cpac.git@feature/progress-tracking

python -m cpac.api -v scheduler --address 0.0.0.0:3333

rm -rf $SCRATCH_DIR/miniconda/

exit 0