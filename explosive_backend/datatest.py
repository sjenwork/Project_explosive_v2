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

dept_e2c = {
    "COA001": "農委會防檢局",
    "EPZA": '"科技產業園區(經濟部加工出口區)"',
    "MND": "國防部",
    "MOEA001": "經濟部中部辦公室",
    "MOEA002": "經濟部工業局(自行設置)",
    "MOEA005": "經濟部礦務局",
    "MOF001": "財政部關務署",
    "MOF002": "財政部國庫署",
    "MOI001": "內政部消防署",
    "MOL001": "勞動部職安署",
    "MOST001": "科技部竹科管理局",
    "MOST002": "科技部中科管理局",
    "MOST003": "科技部南科管理局",
    "MOTC001": "交通部臺灣港務公司",
    "TCSB": "環保署化學局",
    "CAA": "交通部民用航空局",
    "EPA003": "環保署土基會",
}

explosive_list = [
    {'casno': "67-64-1", 'cname': "丙酮", "ename": "acetone"},
    {'casno': "74-86-2", 'cname': "乙炔", "ename": "Acetylene"},
    {'casno': "6484-52-2", 'cname': "硝酸銨", "ename": "Ammonium nitrate"},
    {'casno': "12190-79-3", 'cname': "鋰電池", "ename": "Lithium cobaltate"},
    {'casno': "7439-93-2", 'cname': "鋰", "ename": "Lithium"},
    {'casno': "1333-74-0", 'cname': "氫氣", "ename": "hydrogen"},
    {'casno': "108-88-3", 'cname': "甲苯", 'cname': "methyl-Benzene"},
    {'casno': "67-63-0", 'cname': "異丙醇", "ename": "Isopropanol"},
    {'casno': "7775-09-9", 'cname': "氯酸鈉", "ename": "Sodium chlorate"},
    {'casno': "7803-62-5", 'cname': "矽甲烷", "ename": "Silane"},
    {'casno': "107-13-1", 'cname': "丙烯腈", "ename": "Cyanoethylene"},
    {'casno': "75-21-8", 'cname': "環氧乙烷", "ename": "Ethene oxide"},
    {'casno': "75-56-9", 'cname': "環氧丙烷", "ename": "Propyleneoxide"},
    {'casno': "7722-84-1", 'cname': "過氧化氫", "ename": "Hydrogen peroxide"},
    {'casno': "1338-23-4", 'cname': "過氧化丁酮", "ename": "2-Butanone peroxide"},
]

explosive_n2c = {i['casno']: i['cname'] for i in explosive_list}

pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.unicode.ambiguous_as_wide', True)

client = MongoClient(f"mongodb://localhost:27017/",
                     serverSelectionTimeoutMS=5)
db = client['explosiveNhazardous']
col = db.mergedRecords

query = {"comname": '一旨股份有限公司'}
query = {"comname": '七星化學製藥廠股份有限公司'}
query = {"addr": '新北市土城區福安街七五號'}
df = pd.DataFrame.from_records(list(col.find(query, {'_id': 0})))
df.deptid = df.deptid.map(dept_e2c)
cols = [
    'id',
    'addr', 'addr_merged', 'adminno', 'regno', 'comname', 'comname_merged',
    'casno', 'cat', 'chem_merged', 'cname', 'ename',
    'declaredate', 'declaretime',
    'deptid', 'srcdept',
    'emername', 'emerphone', 'emertel',
    'resname', 'resphone', 'restel',
    'placetype', 'regionname', 'regiontype',

    # 'importCity', 'importQ', 'importX', 'importX2', 'importY', 'importY2',
    # 'prodCity', 'prodQ', 'prodX', 'prodX2', 'prodY', 'prodY2',
    # 'storageCity', 'storageQ', 'storageX', 'storageX2', 'storageY', 'storageY2',
    # 'usageCity', 'usageQ', 'usageX', 'usageX2', 'usageY', 'usageY2'
]



df2 = []
for opt in ['usage', 'storage', 'prod', 'import']:
    mrgkw = ['City', 'X', 'X2', 'Y', 'Y2', 'Q']
    mrgcols = [opt + i for i in mrgkw]
    cols2 = cols + mrgcols
    df2.append(
        df[cols2].rename(columns=dict(zip(mrgcols, mrgkw))
                         ).assign(operation=opt)
    )


operation = 'storage'
chem = '丙酮'
# chem = '異丙醇'

df2 = pd.concat(df2, axis=0)
df2 = df2[df2['Q'] > 0]
# df2.deptid = df2.deptid.map(dept_e2c)

showcols = ['cat', 'declaretime', 'deptid',
            'operation', 'chem_merged', 'cname', 'Q']
df3 = df2[showcols]
df3 = df3[df3.operation == operation]

if operation == 'storage':
    idx = (
        df3
        .groupby(['cat', 'declaretime', 'deptid', 'operation', 'chem_merged'])
        .Q
        .transform(max)
        ==
        df3.Q
    )
    df4 = df3[idx]

    df5 = (
        df4
        .groupby(['cat', 'declaretime', 'deptid', 'operation', 'chem_merged'], as_index=False)
        .agg({
            'Q': sum,
            'cname': lambda i: i.iloc[0],
        })
    )
    df5['cname2'] = df5.chem_merged.map(explosive_n2c)
print(df5[df5.cname == chem])
print(df5[df5.cname2 == chem])
# print(df5)


# test
tmp1 = df[df.deptid=='勞動部職安署']
tmp2 = tmp1[['cat', 'cname', 'ename', 'casno', 'deptid']].sort_values('ename')
