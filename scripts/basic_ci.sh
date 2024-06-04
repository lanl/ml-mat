echo "Activating environment"
source ~/test-env/bin/activate

echo "Running file '$1'"
python3 $1 -v