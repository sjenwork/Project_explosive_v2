import asyncio
from datetime import datetime
import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from src.mongo_tools import get_conn as connMongo
# import pymongo
import socket
import numpy as np
from src.tools import createRandomChn
import copy

pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.unicode.ambiguous_as_wide', True)

app = FastAPI()

origins = [
    # "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    # ComFacBizName_m: str | None = None
    # casno: str | None = None
    # name: str | None = None
    # time: str | None = None
    # deptid: str | None = None
    city: str | None = None


@app.get("/abc")
def test():
    return 'hello world'


@app.get("/explosiveapi_ver2/{colName}")
async def explosive_ver2(
        colName: str,
        method: str = 'all',
        city: str = None,
        ComFacBizName: str = None,
        BusinessAdminNo: str = None,
        name: str = None,
        casno: str = None,
        label: str = None,
        operation: str = None,
        time: int = None,
        time_ge: int | str = None,
        time_le: int | str = None,
        group: str = None,
):
    print(f'\n\n >>>>  查詢時間：{datetime.now()}')
    machineName = 'mongo_chemtest_from_container'
    result = {}
    db = connMongo(machineName)
    if db:
        query = {}
        query_time = ''

        col = db[colName]
        # 廠商
        if ComFacBizName is not None:
            query = query | {'ComFacBizName': {'$regex': ComFacBizName}}
        if BusinessAdminNo is not None:
            query = query | {'BusinessAdminNo': {'$regex': BusinessAdminNo}}
        if group is not None:
            query = query | {'group': group}
        # 化學物質
        if casno is not None:
            query = query | {'casno': casno}
        if name is not None:
            query = query | {'name': name}
        if label is not None:
            query = query | {'label': {'$regex': label}}
        # 運作行為
        if operation is not None:
            query = query | {'operation': operation}
        # 縣市
        if city is not None:
            query = query | {'city': city}
        # 時間
        query_time = {'time': {}}
        if time is not None:
            query_time['time'] = time

        if time_ge is not None:
            if (time_ge != '最新申報') & (time_ge != 'latest'):
                query_time['time']['$gte'] = time_ge
            else:
                query_time = {'$where': "this.time == this.time_latest"}
        if time_le is not None:
            if (time_le != '最新申報') & (time_le != 'latest'):
                query_time['time']['$lte'] = time_le
            else:
                query_time = query_time

        query = query | query_time
        query2 = {}
        for key, val in query.items():
            if val != {}:
                query2[key] = val
        query = query2
        print('query=', query)

        drop_field = ['_id', 'updatetime']
        # if colName == 'ComFacBizHistory_allStatistic':
        #     drop_field += ['city']

        # data = col.find({'name': '丙酮'})
        # print(list(data))
        data = list(col.find(query, dict(
            zip(drop_field, [False]*len(drop_field)))))
        # print(list(data))
        if method == 'statistic':
            if data:
                print('method=statistic')
                data = pd.DataFrame.from_records(data)
                grpcol = list(data.columns.drop(
                    ['time', 'Quantity', 'index', 'time_latest', 'city']))

                storage = copy.deepcopy(data.loc[data.operation == 'storage'])
                storage = (
                    (storage.sort_values(by='Quantity', ascending=False))
                    .groupby(grpcol, as_index=False)
                    .agg({'Quantity': max, 'time': 'first', 'index': lambda i: ','.join(i)})
                )
                other = copy.deepcopy(data.loc[data.operation != 'storage'])
                other = (
                    other.astype({'time': str})
                    .groupby(grpcol, as_index=False)
                    # .agg({'Quantity': sum})
                    .agg({'Quantity': sum, 'time': lambda i: ','.join(sorted(set(i))), 'index': lambda i: ','.join(i)})
                )
                data = pd.concat([storage, other]).to_dict(orient='records')

        elif method == 'city':
            if data:
                data = pd.DataFrame.from_records(data)
                data = data.groupby(['operation', 'city', 'casno',
                                    'cname'], as_index=False).agg({'Quantity': sum})

                if time_le is not None and time_ge is None:
                    time = f'~{time_le}'
                elif time_le is None and time_ge is not None:
                    time = f'{time_ge}'
                elif time_le is not None and time_ge is not None and time_le == time_ge:
                    time = f'{time_ge}'
                else:
                    time = f'{time_ge} - {time_le}'

                data = data.assign(time=time)
                data = data.to_dict(orient='records')
            # data = []

        return list(data)
    else:
        result['status'] = 'server error!'
        return result


@ app.get("/explosiveapi/{kind}")
async def explosive(
        kind: str,
        city: str = None,
        ComFacBizName: str = None,
        name: str = None,
        casno: str = None,
        label: str = None,
        operation: str = None,
        time: int = None,
        time_ge: int | str = None,
        time_le: int | str = None,
        groupid: int = None,
):
    # async def explosive(kind: str):
    # client = pymongo.MongoClient("mongodb://localhost:27017/")
    # db = client["explosive"]
    # machineName = socket.gethostname()
    machineName = 'mongo_chemtest_from_container'
    db = connMongo(machineName)
    if db:
        col = db[kind]
        query = {}
        if ComFacBizName is not None:
            query = query | {'ComFacBizName': {'$regex': ComFacBizName}}
        if casno is not None:
            query = query | {'casno': {'$regex': casno}}
        if name is not None:
            query = query | {'name': {'$regex': name}}
        if label is not None:
            query = query | {'label': {'$regex': label}}
        if operation is not None:
            query = query | {'operation': {'$regex': operation}}
        if city is not None:
            query = query | {'city': {'$regex': city}}
        if time is not None:
            query = query | {'time': time}
        if time_ge is not None:
            if (time_ge != '最新申報') & (time_ge != 'latest'):
                query = query | {'time': {'$gte': time_ge}}
            else:
                query = query
        if time_le is not None:
            if (time_le != '最新申報') & (time_le != 'latest'):
                query = query | {'time': {'$lte': time_le}}
            else:
                query = query
        if groupid is not None:
            query = query | {'group': groupid}

        data = list(col.find(query, {'_id': False}))
        if len(data) > 0:
            if (time_le == '最新申報') | (time_le == 'latest'):
                data = data
            if (time_ge == '最新申報') | (time_ge == 'latest'):
                tmp = pd.DataFrame.from_dict(data)
                if kind == 'statistic_city':
                    res = (
                        tmp[
                            tmp.groupby(
                                ['operation', 'name', 'casno', 'city']
                            ).time.transform(max) == tmp.time]
                    )
                    print(1)
                elif (kind == 'statistic_fac') | (kind == 'statistic_fac_merged'):
                    print(len(tmp), '----1')
                    print(tmp.groupby(
                        ['operation', 'name', 'ComFacBizName']
                    ).time.transform(max))
                    res = (
                        tmp[
                            tmp.groupby(
                                ['operation', 'name', 'ComFacBizName']
                            ).time.transform(max) == tmp.time]
                    )
                    print(len(res), '----2')
                    print(2)
                else:
                    print(3)
                data = res.to_dict(orient='records')
        res = data

        randomizedata = False
        if randomizedata & (kind == 'records_all'):
            tmp = pd.DataFrame.from_dict(res)
            tmp.Quantity = (
                np.round(
                    np.random.random(len(tmp)) ** (np.random.random(len(tmp))*100), 2)
            )
            ComFacBizName = tmp.ComFacBizName.unique()
            ComFacBizName = {i: createRandomChn(len(i)) for i in ComFacBizName}
            # print(ComFacBizName)
            tmp.ComFacBizName = tmp.ComFacBizName.map(ComFacBizName)
            # print(tmp.ComFacBizName)
            # print(tmp.columns)
            # elif kind == 'chemilist':
            #     data = col.find({'label': {'$regex': name}})
            #     return list(data)
            res = tmp.to_dict(orient='records')
        return res
    else:
        return 'server error'
