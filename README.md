# ML Cloud Deployment - Predictive Maintanence

A full stack, cloud deployed machine learning application that predicts equipment failure from sensor readings. 
Built to demonstrate end to end ML pipeline building. <br>

Live App- https://ml-cloud-deployment-k2fwxevsfqmj4ggkcqueaf.streamlit.app/ <br>
API- https://ml-cloud-deployment-zjo4.onrender.com/ <br>
API Docs- https://ml-cloud-deployment-zjo4.onrender.com/docs <br>

What does it do? <br> <br>
A user enters a set of sensor readings: <br>
Type- Machine quality type: Low (L), Medium (M), or High (H) <br>
Ait Temperature (kelvin) <br>
Process Temperature (kelvin) <br>
Rotational Speed (RPM) <br>
Torque (Nm) <br>
Tool Wear (min) <br> <br>
User Recieves: <br>
Prediction on if machine had a failure or not <br>
Probability % that the part failed. <br> <br>

Dataset used - Kaggle Machine Predictive Maintanence Classification <br>
Link: https://www.kaggle.com/datasets/shivamb/machine-predictive-maintenance-classification <br>
Model used - sklearn Random Forest Classifier <br> <br>

Tech Stack <br>
Data store - Supabase (Postgres) - Cloud database for training data and prediction logs <br>
ML tracking - DagsHub + MLflow - Experiment tracking, model versioning, model registry <br>
Model - scikit-learn Random Forest - Binary classification: failure vs. no failure <br>
API - FastAPI + psycopg - REST endpoint for inference, writes predictions to DB <br>
Dashboard - Streamlit - Two page UI prediction form and history table <br>
API Hosting - Render - FastAPI deployment <br>
Dashboard Hosting - Streamlit Community Cloud - Dashboard deployment, connected to GitHub <br>
