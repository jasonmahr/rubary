# Test script.
# Jason Mahr

for run in {1..200}
do
    echo $run

    # Elaborate print statements would have been added to the code.
    # Things printed included constants, results, & times of particular tasks.
    python app.py >> app.csv
done
