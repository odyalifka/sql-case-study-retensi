from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://postgres@localhost:5432/olist_ecommerce')

# Tes tarik data
df = pd.read_sql('SELECT * FROM olist_orders_dataset LIMIT 10', engine)
print(df)