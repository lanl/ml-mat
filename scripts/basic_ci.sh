echo "Activating environment"
module load miniconda3
conda activate mat-env

echo "Running file '$1'"
python3 $1 -v