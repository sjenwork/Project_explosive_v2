import pandas as pd
import pyodbc
from src.sql_tools import get_conn as connSQL

sql = '''SELECT * FROM [ChemiPrimary].[dbo].[ChemiMatchMapping]'''
df = pd.read_sql(sql, con=connSQL('mssql_chemtest'))
