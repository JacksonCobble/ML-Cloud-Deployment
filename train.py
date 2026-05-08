# STDLIB
import os

# Environment
from dotenv import load_dotenv

# Data / IO
import pandas as pd
from sqlalchemy import create_engine

# ML / Modeling
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score

# Experiment Tracking / Logging
import mlflow
import mlflow.sklearn

load_dotenv()

# get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# DagsHub/MLFlow config - set the URI and the username / password token will be setup automatically from .env
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Predictive Maintenance")

print("Pulling data from Supabase...")

# create engine to connect to DB
engine = create_engine(DATABASE_URL)

# use SQL command to pull entire table from DB into pandas dataframe
df = pd.read_sql("SELECT * FROM maintenance_data", engine)
print("Data pulled successfully. Shape:", df.shape)

# since i'm doing a binary classification of this data (failure or not failure)
# rows "failuretype", "udi", and "product_id" are not relevant to the model
df = df.drop(columns=["failure_type", "udi", "product_id"])

# map categorical "type" values to something the random model can use
df["type"] = df["type"].map({"L": 0, "M": 1, "H": 2})

# get features and target values
X = df.drop(columns=["target"])
Y = df["target"]

# constants for model training
N_ESTIMATORS = 100
RANDOM_STATE = 42
TEST_SIZE = 0.2
POSITIVE_CLASS = 1 # the target column value 1 corresponds to a failure

# 80/20 train test split
X_train, x_test, Y_train, y_test = train_test_split(X, Y, test_size=TEST_SIZE, random_state=RANDOM_STATE)

print("Starting model training...")

with mlflow.start_run(run_name="Random Forest Baseline Run"):
    
    # train model and evaluate on test set
    model = RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=RANDOM_STATE)
    model.fit(X_train, Y_train)
    y_pred = model.predict(x_test)

    # evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label=POSITIVE_CLASS, zero_division=0)
    recall = recall_score(y_test, y_pred, pos_label=POSITIVE_CLASS, zero_division=0)

    # print metrics to console down to 4 decimals
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")

    # log parameters used to train model
    mlflow.log_param("n_estimators", N_ESTIMATORS)
    mlflow.log_param("random_state", RANDOM_STATE)
    mlflow.log_param("test_size", TEST_SIZE)
    
    # log evaluation metrics after testing on test set
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)

    # send model to dagshub
    mlflow.sklearn.log_model(
        sk_model= model, 
        artifact_path="random_forest_model", 
        registered_model_name="PredictiveMaintenanceRandomForestModel",
        input_example=x_test[:5] # send first 5 rows of test set as example input for the model in DagsHub UI
        ) 
    
    print("Run logged to DagsHub. Training complete.")