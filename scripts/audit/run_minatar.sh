# usage: run_minatar.sh <folder with the authors' logs>
cd /tmp
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
nice -n 19 $HOME/qwen-control/minatar-env/bin/python /mnt/c/projects/art/qwen-sampling-control/scripts/minatar_control.py "$1/exp5_write_from_scratch/networks" /mnt/c/projects/art/qwen-sampling-control/results_exploratory/minatar.json
