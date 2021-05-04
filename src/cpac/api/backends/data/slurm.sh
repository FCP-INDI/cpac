#!/bin/bash -l

#SBATCH --job-name=$JOB_NAME
#SBATCH --time=$TIME
#SBATCH --nodes=1

# TODO parametrize
SCRATCH_DIR=/tmp/cpacpy-$SLURM_JOBID

_term() {
  echo "Caught SIGTERM signal!"
  kill -TERM "$SERVER" 2>/dev/null
  rm -Rf $SCRATCH_DIR/miniconda $SCRATCH_DIR/miniconda.sh 2>/dev/null
}

trap _term SIGTERM

if [ -d "/opt/miniconda" ] 
then
  source /opt/miniconda/bin/activate
else
  mkdir -p $SCRATCH_DIR
  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O $SCRATCH_DIR/miniconda.sh
  bash $SCRATCH_DIR/miniconda.sh -b -fp $SCRATCH_DIR/miniconda/
  rm $SCRATCH_DIR/miniconda.sh
  source $SCRATCH_DIR/miniconda/bin/activate
fi

PIP_INSTALL=($PIP_INSTALL)
PIP_INSTALL=${PIP_INSTALL:-"git+https://github.com/radiome-lab/cpac.git@feature/progress-tracking"}
pip install "${PIP_INSTALL[@]}"

python -m cpac.api -v scheduler \
  --address 0.0.0.0:3333 \
  --proxy \
  --backend singularity \
  --singularity-image $IMAGE &

SERVER=$!
while kill -0 $SERVER 2> /dev/null; do
  sleep 1
done

exit 0
