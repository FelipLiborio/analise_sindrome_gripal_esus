from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql://esus_user:esus_password@localhost:5432/esus_gripal")

def query(sql):
    return pd.read_sql(sql, engine)
