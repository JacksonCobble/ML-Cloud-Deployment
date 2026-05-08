# STDLIB
import os
from datetime import datetime, timezone

# Environment
from dotenv import load_dotenv

# API / Validation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
