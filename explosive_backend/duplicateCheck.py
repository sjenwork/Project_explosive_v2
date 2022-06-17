from inspect import getframeinfo, stack
import pandas as pd
import geopandas as gpd
from fastapi import FastAPI, Request
from pymongo import UpdateMany, UpdateOne, InsertOne
from pymongo import MongoClient
import re
import copy
from tqdm import tqdm
from enum import Enum
from fastapi.responses import HTMLResponse
from src.sql_tools import get_conn as connSQL
import numpy as np

pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.unicode.ambiguous_as_wide', True)

client = MongoClient(f"mongodb://localhost:27017/",
                     serverSelectionTimeoutMS=5)
# client = MongoClient(f"mongodb://172.18.18.4:27017/",
#                          serverSelectionTimeoutMS=5)
db = client['explosiveNhazardous']
col = db.mergedRecords
data = list(col.find({}, {'_id': 0}))
data2 = pd.DataFrame.from_records(data)

data3 = data2.groupby(['comname_merged']).agg(
    {
        'deptid': lambda i: ','.join(set(i)),
        'regiontype': lambda i: ','.join(set(i)),
    }
    )
data4 = data3[data3.regiontype.str.contains(',')]
