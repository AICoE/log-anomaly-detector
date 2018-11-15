
# Validation Data

The purpose of this code is to provide users a simple way to get access to data and run the app 
locally for testing and verification.  

#### The Data Set

The script `generate_validation_data.py` collects **80,000** logs from the service of your choice hosted at your Elasticsearch endpoint in the index you define.  

Of the 80,000 logs, the training set is unchanged at constitutes **80% of the dataset (64,000 logs)** and the test set makes up the remaining **20% (16,000 logs)**

The test set was genereated by randomly selecting **10% of the training data (~1,600)** and replacing it with random character strings.

The output files **verification_data_new.json** and **labels_new.pkl** are saved to the current directory


#### How to download local test data

Set the correct environment variables for your Elasticsearch endpoint, index and service you want to pull data from.

````
export LAD_ENDPOINT="<your endpoint>" 
export LAD_INDEX="<your index>"
export LAD_SERVICE="<your service>"
````

Run the script `generate_validation_data.py`

````
python generate_validation_data.py
````
If this ran correctly you should see the following output:

````
80000 logs and corresponding labels saved to disk as verification_data.json and labels.pkl
```` 

The verification_data.json and labels.pkl are now stored locally for testing with the anomaly detector using the default local backend.

#### How to run a local test 

Set the correct environment variables for your local data location and output file.

````
export LOCAL_DATA_FILE="validation_data/verification_data.json"
export LOCAL_RESULTS_FILE="results.json"
```` 

From the root directory run `app.py`.

````
python app.py
````

This will kick of a training and inference loop, printing status and found anomlies to the terminal. 

Since this is a static dataset meant for local validation and testing. You should `ctrl+c` out of the program after the first infrence loop as no additional data is being passed in.

With the `results.json` and `labels.pkl` you can check the ability of the current anomaly detector (with current parameters) 
to detect our generated anomalies of random character strings offline. Future iteration of this tool will include some additional validation capabilities.       