# STDLIB
import os
from datetime import datetime, timezone
from pyexpat import features

# Environment
from dotenv import load_dotenv

# API / Validation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

# Database
import psycopg2

# Experiment Tracking / Model Registry
import mlflow
import mlflow.sklearn
import dagshub


load_dotenv()

# set up mlflow dagshub link
dagshub.init(repo_owner=os.getenv("MLFLOW_TRACKING_USERNAME"), repo_name="ML-Cloud-Deployment", mlflow=True)

# set the URI and the username / password token will be setup automatically from .env
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

# load model from mlflow model registry
model_name = os.getenv("MLFLOW_MODEL_NAME")
# this string is formatted to take the generic model name and pull the one that has its alias set on mlflow as "champion"
model_uri = f"models:/{model_name}/2"
model = mlflow.sklearn.load_model(model_uri)

# encoding for the categorical "type" feature
TYPE_MAP = {"L": 0, "M": 1, "H": 2}

# make FastAPI app
app = FastAPI(title="Predictive Maintenance API", description="API for predicting machine failure based on sensor data", version="1.0")

# sanity check to make sure server is actually RUNNING
@app.get("/isrunning")
def is_running():
    return {"message": "API is running!"}

# pydantic model for input validation - note: we are using pydantic because it is used to validate, parse, and
# structure data without having to worry about it. we can define an expected schema, and pydantic will enforce it
class SensorData(BaseModel):
    type: str
    air_temperature: float
    process_temperature: float
    rotational_speed: int
    torque: float
    tool_wear: int

# predict function/endpount - this is how the rest API will recieve data and return predictions.
# note- pydantic will automatically take the JSON being recieved and convert it to the sensordata class
@app.post("/predict")
def predict(data: SensorData):
    # we need to validate that the string input for type is one of the 3 letters otherwise 
    # we cant map it to an integer for the model
    if data.type not in TYPE_MAP:
        # status code 400 - bad request, data being sent is not valid.
        raise HTTPException(status_code=400, detail="Invalid type. Must be one of 'L', 'M', or 'H'.")
    
    # transform data into a form that the model can use
    # IMPORTANT: the format of the actual features being sent needs to be in the EXACT for that the model was originally trained on.
    # the error given will not make sense and cause a generational crashout
    features = pd.DataFrame([{
        "type": TYPE_MAP[data.type],
        "air_temperature_[k]": data.air_temperature,
        "process_temperature_[k]": data.process_temperature,
        "rotational_speed_[rpm]": data.rotational_speed,
        "torque_[nm]": data.torque,
        "tool_wear_[min]": data.tool_wear
    }])

    # run prediction on model
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    label = "Failure" if prediction == 1 else "No Failure"

    # return the prediction and probability
    return {
        "prediction": prediction,
        "probability": round(probability, 4),
        "label": label
    }