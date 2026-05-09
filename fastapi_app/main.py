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
# using psycopg instead of sqlalchemy (which is just a wrapper for psycopg2 because
# since this is going to be on a server that taken in queries we want it to be as lean
# as possible aka minimum overhead
import psycopg 


# Experiment Tracking / Model Registry
import mlflow
import mlflow.sklearn
# import dagshub


load_dotenv()

# set up mlflow dagshub link
# dagshub.init(repo_owner=os.getenv("MLFLOW_TRACKING_USERNAME"), repo_name="ML-Cloud-Deployment", mlflow=True)

# set the URI and the username / password token will be setup automatically from .env
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

# load model at startup
model = None
try:
    model_name = os.getenv("MLFLOW_MODEL_NAME")
    # this string is formatted to take the generic model name and pull the one that is version "2".
    # for some reason trying to get the alias "@champion" does not work.
    model_uri = f"models:/{model_name}/2"
    model = mlflow.sklearn.load_model(model_uri)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model loading failure: {e}")

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
    # make sure model loaded successfully
    if model is None:
        # status code 503 - service unavailable, api running but model service is out
        raise HTTPException(status_code=503, detail="Model not available. Try again later.")
    
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
    try:
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        label = "Failure" if prediction == 1 else "No Failure"
    except Exception as e:
        # status code 500- internal service error. the request worked fine, theres just something wrong with the algorithm its calling.
        raise HTTPException(status_code=500, detail="Prediction failed")

    # log info back to our database in a new table "predictions"
    try:
        # psyopg2 lets us connect to a database and send it SQL
        conn = psycopg.connect(os.getenv("DATABASE_URL"))
        # cursor is the object that is capable of talking to the sql server
        cur = conn.cursor()
        # execute this SQL into the database
        cur.execute("""
            INSERT INTO predictions (
                type, air_temperature, process_temperature,
                rotational_speed, torque, tool_wear,
                prediction, prediction_label, probability_failure
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            TYPE_MAP[data.type],
            data.air_temperature,
            data.process_temperature,
            data.rotational_speed,
            data.torque,
            data.tool_wear,
            prediction,
            label,
            probability
        ))
        # changes are temporary until committed like a repo, so you need to commit the changes to the database
        conn.commit()
        # close sql worker and hang up db connection
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Supabase logging error: {e}")

    # return the prediction and probability
    return {
        "prediction": prediction,
        "probability": round(probability, 4),
        "label": label
    }