import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# This file is used as the intial seeding of the Supabase Postgres DB being used
# It reads the CSV file containing our intitial load of data and uses SQLAlchemy engine
# to connect to the hosted postgres server and upload that CSV file's information.

# load dotenv to get environment variables
load_dotenv()

# remember that the URI value from Supabase needs to NOT be the direct URI,
# but instead needs to be the transaction pooler URI
DATABASE_URL = os.getenv("DATABASE_URL")

# engine object to actually connect to our hosted db to interact with it
engine = create_engine(DATABASE_URL)

# load CSV file into a pandas DataFrame
df = pd.read_csv("data/predictive_maintenance.csv")

# replace column names with lowercase verions, where spaces are replaced with underscores
df.columns = df.columns.str.lower().str.replace(" ", "_")

# sanity check prints
print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print(df.head())

# write dataframe to Supabase
with engine.connect() as conn:
    df.to_sql("maintenance_data", conn, if_exists="replace", index=False)
    print("Data uploaded successfully")