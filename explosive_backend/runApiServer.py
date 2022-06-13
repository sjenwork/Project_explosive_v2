from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pymongo import UpdateMany, UpdateOne, InsertOne
from src.mongo_tools import get_conn as connMongo
from src.tools import createRandomChn
from inspect import getframeinfo, stack
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import geopandas as gpd
from typing import Union
import numpy as np
from tqdm import tqdm
from enum import Enum
import asyncio
import socket
import copy
import json
import re


pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.unicode.ambiguous_as_wide', True)


def print2(message, path='rel'):
    caller = getframeinfo(stack()[1][0])
    fn = caller.filename
    no = caller.lineno
    if path == 'rel':
        fn = fn.split('/')[-1]
    print(f' >> {message}     <-- {fn}:{no}')


tags_metadata = [
    {
        'name': '易爆物與高風險化學物質 ver4',
        "description": '易爆物與高風險化學物質APIs_ver4',
    },
    {
        'name': '易爆物與高風險化學物質 ver3',
        "description": '易爆物與高風險化學物質APIs_ver3',
    }
]

app = FastAPI(openapi_tags=tags_metadata,
              root_path="/demo/chemicloud/explosive")

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


# class Item(BaseModel):
#     # ComFacBizName_m: str | None = None
#     # casno: str | None = None
#     # name: str | None = None
#     # time: str | None = None
#     # deptid: str | None = None
#     city: str | None = None

rawCols = [
    'casno',
    'cname',
    'ename',
    'srcdept',
    'deptid',
    'resname',
    'restel',
    'resphone',
    'emername',
    'emertel',
    'emerphone',
    'comname',
    'adminno',
    'regno',
    'addr',
    'placetype',
    'regiontype',
    'regionname',
    'importX',
    'importY',
    'declaretime',
    'importQ',
    'prodQ',
    'prodX',
    'prodY',
    'usageQ',
    'usageX',
    'usageY',
    'storageQ',
    'storageX',
    'storageY',
    'cat'
    # 'DeptID',化學物質中文名
    # 'declaretime',
]

col_map = {
    'casno': 'CAS No.',
    'cname': '化學物質中文名',
    'ename': '化學物質英文名',
    'srcdept': '資料來源',
    'resname': '聯絡資料：\r\n公司負責人',
    'restel': '聯絡資料：\r\n聯絡電話',
    'resphone': '聯絡資料：\r\n手機號碼',
    'emername': '聯絡資料：\r\n緊急連絡人',
    'emertel': '聯絡資料：\r\n緊急連絡人電話',
    'emerphone': '聯絡資料：\r\n緊急連絡人手機',
    'comname': '廠商基本資料：\r\n公司/工廠名稱',
    'adminno': '廠商基本資料：\r\n統一編號(8碼)',
    'regno': '廠商基本資料：\r\n工廠登記證號',
    'addr': '廠商基本資料：\r\n地址',
    'placetype': '廠商基本資料：\r\n運作場所型態備註(工廠/倉庫)',
    'regiontype': '廠商基本資料：\r\n廠商所在區域類別(科學園區/工業區/加工出口區/港區/其他)',
    'regionNname': '廠商基本資料：\r\n廠商所在區域名稱(科學園區/工業區/加工出口區/港區/其他)',
    'importX': '廠商地址座標資訊\r\n TWD97_X',
    'importY': '廠商地址座標資訊\r\n TWD97_Y',
    'declaretime': '申報年月',
    'importQ': '輸入量',
    'prodQ': '製造量',
    'prodX': '製造地點座標資訊\r\n TWD97_X',
    'prodY': '製造地點座標資訊\r\n TWD97_Y',
    'usageQ': '使用量',
    'usageX': '使用地點座標資訊\r\n TWD97_X',
    'usageY': '使用地點座標資訊\r\n TWD97_Y',
    'storageQ': '貯存量',
    'storageX': '貯存地點座標資訊\r\n TWD97_X',
    'storageY': '貯存地點座標資訊\r\n TWD97_Y',
    'deptid': '部會名稱'
    # 'declaretime',
}


@app.get("/test", tags=['test'])
def test():
    return 'hello world'


@app.get("/explosiveapi_ver2/{colName}", tags=['易爆物與高風險化學物質 ver2'])
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


@ app.get("/explosiveapi/{kind}", tags=['易爆物與高風險化學物質'])
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


class sourceModel(str, Enum):
    mergedRecords = 'mergedRecords'
    chemical_list = 'chemical_list'
    company_list = 'company_list'


class sourceModel2(str, Enum):
    mergedRecords = 'mergedRecords'


class typeModel(str, Enum):
    data_list = 'data_list'
    chemical_list = 'chemical_list'
    company_list = 'company_list'
    time_list = 'time_list'
    city_count = 'city_count'


class operationModel(str, Enum):
    usage = 'usage'
    storage = 'storage'
    prod = 'prod'
    importing = 'import'


@app.get("/explosiveapi_ver4/{data_source}/{data_type}", tags=['易爆物與高風險化學物質 ver4'])
def datalist2(
    data_source: sourceModel2,
    data_type: typeModel,
    company_name: str = None,
    chemical_name: str = None,
    operation: operationModel = None,
    offset: int = 0,
    limit: int = 20,
    display: bool = True,
    time: str = None,
    time_ge: str = None,
    time_le: str = None,
    time_latest: bool = False,
    to_html: bool = False
):

    # client = MongoClient(f"mongodb://localhost:27017/",
    client = MongoClient(f"mongodb://172.18.18.4:27017/",
                         serverSelectionTimeoutMS=5)
    db = client['explosiveNhazardous']
    col = db[data_source]

    if data_type == 'data_list' or data_type == 'city_count':
        query = {}
        query_time = {'declaretime': {}}
        constraint = {'_id': 0}

        if chemical_name is not None:
            chemical_name = (
                chemical_name
                .replace('(','\(')
                .replace(')','\)')
                )            
            query = (query | {'chem_merged': {'$regex': chemical_name}})

        if company_name is not None:
            company_name = (
                company_name
                .replace('(','\(')
                .replace(')','\)')
                )
            query = (query | {'comname_merged': {'$regex': company_name}})

        if not time_latest:
            if time is not None:
                query_time['declaretime'] = time
            if time_ge is not None:
                query_time['declaretime']['$gte'] = time_ge
            if time_le is not None:
                query_time['declaretime']['$lte'] = time_le
            if query_time['declaretime'] != {}:
                query = query | query_time
        else:
            pass
            # 最新期別的資料，會將資料完整讀出後，再做處理！

        print('query: ', query)

        # if (time is None and time_ge is None and time_le is None and not time_latest):
        #     return {'status': '此種查詢方法不符合需求，請給定「時間範圍」！'}

        if (operation is None or chemical_name is None) and (company_name is None):
            return {
                'status': ''' 此種查詢方法不符合需求。 化學物質查詢，請給「運作行為」與「化學物質」; 廠商查詢，請給定「廠商名稱」。 '''
            }

        #  --------------------------------------------  網頁呈現  --------------------------------------------
        if display:
            constraint = (
                constraint |
                {
                    'id': 0,
                    'emername': 0,
                    'emerphone': 0,
                    'emertel': 0,
                    'restel': 0,
                    'resphone': 0,
                    'resname': 0,
                    'placetype': 0,
                    'regionNname': 0,
                    'importX': 0,
                    'importY': 0,
                    'usageX': 0,
                    'usageY': 0,
                    'storageX': 0,
                    'storageY': 0,
                    'prodX': 0,
                    'prodY': 0,
                    'addr_merged': 0,
                    'srcdept': 0,

                    # 'comname_merged': 0,
                    # 'chem_merged': 0,
                    # 'declaretime': 0,
                }
            )
            data = col.find(query, constraint)
            data = list(data)
            # print(data[0])
            print()
            print2(f'搜尋條件：{query}')
            print2(f'找到共 {len(data)} 筆')
            print()
            # print(pd.DataFrame.from_dict(data).T)
            if len(data) == 0:
                return []

            data2 = pd.DataFrame.from_records(data).fillna('-')
            # print(data2.T)
            #  -----------------------------------------------------------------------------------------------
            #  運作化學物質廠商查詢
            if operation is not None:
                stat_cols = [
                    'comname', 'addr', 'adminno', 'regno', 'casno',
                    'cname', 'ename',  'declaretime',
                    'comname_merged', 'chem_merged',
                    'regiontype', 'deptid', 'cat'
                ] + [
                    f"{operation}Q",
                    f"{operation}X2",
                    f"{operation}Y2",
                    f'{operation}City',
                ]
                data2 = data2[stat_cols]
                data2 = data2.fillna('-')
                # print(data2.iloc[0])

                #  -------------------------------------------------------------------------------------------
                #  運作化學物質廠商查詢 -> 查詢期別區間
                if not time_latest:
                    #  ---------------------------------------------------------------------------------------
                    #  運作化學物質廠商查詢 -> 查詢期別區間 -> 非貯存（統計加總）
                    if operation != 'storage':
                        data2 = (
                            data2
                            .groupby(
                                [
                                    'cat', 'deptid', 'comname_merged', 'regiontype', 'cname',
                                    f"{operation}X2", f"{operation}Y2", f"{operation}City",
                                ],
                                as_index=False
                            )
                            .agg(
                                {
                                    f"{operation}Q": sum,
                                    "adminno": lambda i: ','.join(set(i)),
                                    "regno": lambda i: ','.join(set(i)),
                                    "addr": lambda i: ','.join(set(i)),
                                    "comname": lambda i: i.iloc[0],
                                    "cname": lambda i: i.iloc[0],
                                    "ename": lambda i: i.iloc[0],
                                    "casno": lambda i: i.iloc[0],
                                    "declaretime": lambda i: ','.join(set(i)),
                                    # "declaretime": lambda i: f"{time_ge if time_ge else '_'} -> {time_le if time_le else '_'}",
                                    "chem_merged": lambda i: ','.join(set(i)),
                                }
                            )
                            .assign(operation=operation.name)
                            .rename(columns={
                                f'{operation}X2': 'X',
                                f'{operation}Y2': 'Y',
                                f'{operation}Q': 'Q',
                                f'{operation}City': 'City',
                            })
                        )
                        print2(
                            f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['declaretime']} }} 查詢")
                        print2(f"統計後共 {len(data2)} 筆")
                        print()
                        print2(data2)
                    #  運作化學物質廠商查詢 -> 查詢期別區間 -> 非貯存（統計加總）end
                    #  ---------------------------------------------------------------------------------------

                    #  ---------------------------------------------------------------------------------------
                    #  運作化學物質廠商查詢 -> 查詢期別區間 -> 貯存（最大值與最大期別）
                    else:
                        # -> 依照運作量
                        idx = (
                            data2
                            .groupby(
                                [
                                    'cat', 'deptid', 'comname_merged', 'regiontype', 'cname',
                                    f"{operation}X2", f"{operation}Y2", f"{operation}City",
                                ]
                            )[f"{operation}Q"]
                            .transform(max)
                            ==
                            data2[f"{operation}Q"]
                        )
                        data2 = data2[idx]
                        print2('選擇較最大的')
                        print2(
                            f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['declaretime']} }} 查詢")
                        print2(f"統計後共 {len(data2)} 筆")
                        print()
                        # -> 若運作量相同，選擇較新的
                        idx = (
                            data2
                            .groupby(
                                [
                                    'cat', 'deptid', 'comname_merged', 'regiontype', 'cname',
                                    f"{operation}X2", f"{operation}Y2", f"{operation}City",
                                ]
                            )["declaretime"]
                            .transform(max)
                            ==
                            data2["declaretime"]
                        )
                        data2 = data2[idx]

                        # -> 同期別加總

                        data2 = (
                            data2
                            .groupby(
                                [
                                    'cat', 'deptid', 'comname_merged', 'regiontype', 'cname',
                                    f"{operation}X2", f"{operation}Y2", f"{operation}City",
                                ],
                                as_index=False
                            ).agg(
                                {
                                    f"{operation}Q": sum,
                                    "adminno": lambda i: ','.join(set(i)),
                                    "regno": lambda i: ','.join(set(i)),
                                    "addr": lambda i: ','.join(set(i)),
                                    "comname": lambda i: i.iloc[0],
                                    "cname": lambda i: i.iloc[0],
                                    "ename": lambda i: i.iloc[0],
                                    "casno": lambda i: i.iloc[0],
                                    "declaretime": lambda i: ','.join(set(i)),
                                    "chem_merged": lambda i: ','.join(set(i)),
                                }
                            )

                        )

                        print2('選擇較新的')
                        print2(
                            f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['declaretime']} }} 查詢")
                        print2(f"統計後共 {len(data2)} 筆")
                        print()

                        data2 = (
                            data2
                            .reset_index(drop=True)
                            .assign(operation=operation.name)
                            .rename(columns={
                                f'{operation}X2': 'X',
                                f'{operation}Y2': 'Y',
                                f'{operation}Q': 'Q',
                                f'{operation}City': 'City',
                            })
                        )
                        print2(
                            f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['declaretime']} }} 查詢")
                        print2(f"統計後共 {len(data2)} 筆")
                        print()
                        # print2(data2[['deptid', 'X', 'Y', 'City', 'operation']])
                    #  運作化學物質廠商查詢 -> 查詢期別區間 -> 貯存（最大值與最大期別） end
                    #  ---------------------------------------------------------------------------------------
                #  運作化學物質廠商查詢 -> 查詢期別區間 end
                #  -------------------------------------------------------------------------------------------

                #  -------------------------------------------------------------------------------------------
                #  運作化學物質廠商查詢 -> 最新期別查詢
                else:
                    idx = (
                        data2
                        .groupby(
                            [
                                'cat', 'deptid', 'comname_merged', 'regiontype', 'cname',
                                f"{operation}X2", f"{operation}Y2", f"{operation}City",
                            ]
                        )[f"declaretime"]
                        .transform(max)
                        ==
                        data2["declaretime"]
                    )

                    data2 = (
                        data2[idx]
                        .groupby(
                            [
                                'cat', 'deptid', 'comname_merged', 'regiontype', 'cname',
                                f"{operation}X2", f"{operation}Y2", f"{operation}City",
                            ],
                            as_index=False,
                        )
                        .agg(
                            {
                                f"{operation}Q": sum,
                                "adminno": lambda i: ','.join(set(i)),
                                "regno": lambda i: ','.join(set(i)),
                                "addr": lambda i: ','.join(set(i)),
                                "comname": lambda i: i.iloc[0],
                                "cname": lambda i: i.iloc[0],
                                "ename": lambda i: i.iloc[0],
                                "casno": lambda i: i.iloc[0],
                                "declaretime": lambda i: ','.join(set(i)),
                                "chem_merged": lambda i: ','.join(set(i)),
                            }
                        )
                        .reset_index(drop=True)
                        .assign(operation=operation.name)
                        .rename(columns={
                            f'{operation}X2': 'X',
                            f'{operation}Y2': 'Y',
                            f'{operation}Q': 'Q',
                            f'{operation}City': 'City',
                        })
                    )
                    # return {'status': '查詢最新運作量'}
                    print2(
                        f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: latest }} 查詢")
                    print2(f"統計後共 {len(data2)} 筆")
                    print()

                data2 = data2[[
                    'cat', 'declaretime', 'deptid', 'comname_merged', 'comname', 'regiontype', 'addr', 'adminno', 'regno',
                    'cname', 'ename', 'casno', 'chem_merged',
                    'operation', 'X', 'Y',  "Q", "City"
                ]]
                data2 = data2.sort_values(by=[
                    'cat', 'deptid',  'Q', 'regiontype', 'comname_merged'
                ], ascending=[
                    True, True,  False, True, True
                ])
                #  運作化學物質廠商查詢 -> 最新期別查詢 end
                #  -------------------------------------------------------------------------------------------
            #  運作化學物質廠商查詢 end
            #  -----------------------------------------------------------------------------------------------

            #  -----------------------------------------------------------------------------------------------
            # 廠商查詢運作化學物質
            else:
                #  -------------------------------------------------------------------------------------------
                #  廠商查詢運作化學物質 -> 查詢期別區間
                if not time_latest:
                    # return {'status': '查詢廠商運作量統計'}
                    data2 = data2.set_index([
                        'cat', 'declaretime', 'deptid', 'comname_merged', 'comname', 'regiontype', 'addr', 'adminno', 'regno',
                        'cname', 'ename', 'casno', 'chem_merged',
                    ])
                    data3 = []
                    #  ---------------------------------------------------------------------------------------
                    #  wide to long
                    for ioperation in ['storage', 'usage', 'prod', 'import']:
                        tmp = data2[
                            [
                                f'{ioperation}X2',
                                f'{ioperation}Y2',
                                f'{ioperation}Q',
                                f'{ioperation}City',
                            ]
                        ].rename(
                            columns={
                                f'{ioperation}X2': 'X',
                                f'{ioperation}Y2': 'Y',
                                f'{ioperation}Q': 'Q',
                                f'{ioperation}City': 'City'
                            }
                        ).assign(
                            operation=ioperation,
                        )

                        data3.append(tmp)
                    data2 = pd.concat(data3).reset_index()
                    data2 = data2[data2['Q'] > 0]
                    #  ---------------------------------------------------------------------------------------

                    #  ---------------------------------------------------------------------------------------
                    #  廠商查詢運作化學物質 -> 查詢期別區間 -> 處理貯存
                    data2_storage = data2[data2.operation == 'storage']
                    #  --> 只有在有資料時才做以下處理
                    if len(data2_storage) > 0:
                        #  --> 先依據貯存量，貯存量從大
                        idx = (
                            data2_storage
                            .groupby(
                                ['cat', 'deptid', 'cname', 'comname',
                                    'regiontype', 'operation']
                            )['Q']
                            .transform(max) == data2_storage.Q
                        )
                        data2_storage = data2_storage[idx]

                        #  --> 貯存量相同，時間從新
                        idx = (
                            data2_storage
                            .groupby(
                                ['cat', 'deptid', 'cname', 'comname',
                                    'regiontype', 'operation']
                            )['declaretime']
                            .transform(max) == data2_storage.declaretime
                        )
                        data2_storage = data2_storage[idx]

                        data2_storage = (
                            data2_storage
                            .groupby(
                                [
                                    'cat', 'deptid',
                                    'comname_merged', 'regiontype', 'addr', 'X', 'Y', 'City',
                                    'chem_merged', 'operation',
                                ],
                                as_index=False
                            ).agg({
                                "Q": sum,
                                "adminno": lambda i: ','.join(set(i)),
                                "regno": lambda i: ','.join(set(i)),
                                "comname": lambda i: i.iloc[0],
                                "cname": lambda i: i.iloc[0],
                                "ename": lambda i: i.iloc[0],
                                "casno": lambda i: i.iloc[0],
                                "declaretime": lambda i: ','.join(set(i)),
                            })
                        )

                    #
                    #
                    #  ---------------------------------------------------------------------------------------

                    #  ---------------------------------------------------------------------------------------
                    #  廠商查詢運作化學物質 -> 查詢期別區間 -> 處理貯存之外的
                    data2_others = data2[data2.operation != 'storage']
                    # --> 只有在有資料時才做以下處理
                    if len(data2_others) > 0:
                        data2_others = (
                            data2_others
                            .groupby(
                                [
                                    'cat', 'deptid',
                                    'comname_merged', 'regiontype', 'addr', 'X', 'Y', 'City',
                                    'chem_merged', 'operation',
                                ],
                                as_index=False
                            ).agg({
                                "Q": sum,
                                "adminno": lambda i: ','.join(set(i)),
                                "regno": lambda i: ','.join(set(i)),
                                "comname": lambda i: i.iloc[0],
                                "cname": lambda i: i.iloc[0],
                                "ename": lambda i: i.iloc[0],
                                "casno": lambda i: i.iloc[0],
                                "declaretime": lambda i: ','.join(set(i)),
                            })
                        )
                    #  ---------------------------------------------------------------------------------------

                    data2 = pd.concat([data2_storage, data2_others])
                    data2 = data2.fillna('-').reset_index(drop=True)

                    # print(data2)
                    print2(
                        f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['declaretime']} }} 查詢")
                    print2(f"統計後共 {len(data2)} 筆")
                    print()
                #  廠商查詢運作化學物質 -> 查詢期別區間 end
                #  -------------------------------------------------------------------------------------------

                #  -------------------------------------------------------------------------------------------
                #  廠商查詢運作化學物質 -> 查詢最新期別
                else:
                    # return {'status': '查詢廠商最新運作量'}
                    # 找出最新的期別
                    idx = (
                        data2
                        .groupby(
                            [
                                'cat', 'deptid', 'regiontype', 'chem_merged', 'addr',
                            ]
                        )[f"declaretime"]
                        .transform(max)
                        ==
                        data2["declaretime"]
                    )

                    data2 = (data2[idx])

                    # ['declaretime', 'srcdept', 'deptid', 'comname_merged', 'comname', 'regiontype',
                    # 'addr', 'adminno', 'regno', 'cname', 'ename',
                    # 'casno', 'chem_merged',  'X',
                    # 'Y', 'Q', 'operation']
                    # 14 + 3*4 = 26 -> 14 + 3 + 1= 18

                    # 將運作量 wide to long
                    data2 = data2.set_index([
                        'declaretime', 'cat', 'deptid', 'comname_merged', 'comname', 'regiontype',
                        'addr', 'adminno', 'regno', 'cname', 'ename',
                        'casno', 'chem_merged',
                    ])
                    data3 = []
                    for ioperation in ['storage', 'usage', 'prod', 'import']:
                        tmp = data2[
                            [
                                f'{ioperation}X2',
                                f'{ioperation}Y2',
                                f'{ioperation}Q',
                                f'{ioperation}City',
                            ]
                        ].rename(
                            columns={
                                f'{ioperation}X2': 'X',
                                f'{ioperation}Y2': 'Y',
                                f'{ioperation}Q': 'Q',
                                f'{ioperation}City': 'City'
                            }
                        ).assign(
                            operation=ioperation,
                        )

                        data3.append(tmp)
                    data2 = pd.concat(data3).reset_index()
                    data2 = data2[data2['Q'] > 0]
                    print2(data2)
                    if len(data2) > 0:
                        data2 = (
                            data2
                            .groupby(
                                [
                                    'cat', 'deptid',
                                    'comname_merged', 'regiontype', 'addr', 'X', 'Y', 'City',
                                    'chem_merged', 'operation',
                                ],
                                as_index=False
                            )
                            .agg({
                                "Q": sum,
                                "adminno": lambda i: ','.join(set(i)),
                                "regno": lambda i: ','.join(set(i)),
                                "comname": lambda i: i.iloc[0],
                                "cname": lambda i: i.iloc[0],
                                "ename": lambda i: i.iloc[0],
                                "casno": lambda i: i.iloc[0],
                                "declaretime": lambda i: ','.join(set(i)),
                            })
                            .reset_index(drop=True)
                        )

                        data2 = data2.fillna('-').reset_index(drop=True)

                    print2(
                        f"廠商查詢運作化學物質 -> {{ chem: {chemical_name}, operation: {operation}, time: latest }} 查詢")
                    print2(f"統計後共 {len(data2)} 筆")
                    print()
                    # return {}
                #  廠商查詢運作化學物質 -> 查詢最新期別 end
                #  -------------------------------------------------------------------------------------------
                data2 = data2[[
                    'declaretime', 'cat', 'deptid', 'comname_merged', 'comname', 'regiontype', 'addr', 'adminno', 'regno',
                    'cname', 'ename', 'casno', 'chem_merged',
                    'operation', 'X', 'Y', "Q", "City"

                ]]
                data2 = data2.astype(object)
                data2 = data2.where(pd.notnull(data2), None)
                data2 = data2.sort_values(by=[
                    'cat', 'deptid', 'chem_merged', 'operation', 'Q'
                ])
                # data2[data2.isna] = None

            if data_type == 'city_count':
                # print2(len(data2.columns))
                # print2((data2.columns))
                # [
                #     'cat', 'declaretime', 'deptid', 'comname_merged', 'comname',
                #     'regiontype', 'addr', 'adminno', 'regno', 'cname', 'ename', 'casno',
                #     'chem_merged', 'operation', 'X', 'Y', 'Q', 'City'
                # ]
                stat = data2.groupby(
                    ['City', 'operation'], as_index=False) .Q.agg(sum)
                return stat.to_dict(orient='records')

            if to_html:
                return HTMLResponse(content=data2.to_html(), status_code=200)
            else:
                return data2.to_dict(orient='records')
            # 廠商查詢運作化學物質 end
            #  -----------------------------------------------------------------------------------------------
            return data2.to_html()
            return data2.to_dict(orient='records')
        #  --------------------------------------------  網頁呈現  --------------------------------------------

        #  --------------------------------------------  資料下載  --------------------------------------------
        else:
            # 資料下載（原始資料）
            constraint = {
                '_id': 0
            }
            # .skip(offset).limit(limit)
            data = list(col.find(query, constraint))

            data2 = (
                pd.DataFrame
                .from_records(data)#[rawCols]
                # .rename(columns=col_map)
                .fillna('-')
                # .astype(object)
            )
            # data2 = data2.where(pd.notnull(data2), None)
            # return {}
            return data2.to_dict(orient='records')
        #  --------------------------------------------  資料下載  --------------------------------------------

    elif data_type == 'chemical_list':
        query = [{}]
        if chemical_name is not None:
            query = [
                {'cname': {'$regex': chemical_name}},
                {'ename': {'$regex': chemical_name}},
                {'casno': {'$regex': chemical_name}},
            ]
        data = col.aggregate(
            [
                {
                    '$match': {
                        '$or': query
                    }
                },
                {
                    "$group": {
                        "_id":
                        {
                            'cat': '$cat',
                            'casno': '$casno',
                            'cname': '$cname',
                            'ename': "$ename",
                            'chem_merged': '$chem_merged',
                        }
                    }
                },
                {"$sort": {"_id.casno": 1}},
                {"$skip": offset},
                {"$limit": limit}
            ])
        data = [i['_id'] for i in data]
        return list(data)

    elif data_type == 'company_list':
        query = [{}]
        if company_name is not None:
            query = [
                {'comname': {'$regex': company_name}},
                {'regno': {'$regex': company_name}},
                {'adminno': {'$regex': company_name}},
            ]
        data = col.aggregate(
            [
                {
                    '$match': {
                        '$or': query
                    }
                },
                {
                    "$group": {
                        "_id":
                        {
                            'comname': '$comname',
                            # 'addr': '$addr',
                            'regno': '$regno',
                            'adminno': "$adminno",
                            'comname_merged': '$comname_merged',
                        }
                    }
                },
                {"$sort": {"_id.comname": 1}},
                {"$skip": offset},
                {"$limit": limit}
            ])
        data = [i['_id'] for i in data]
        return list(data)

    elif data_type == 'time_list':
        query = [{}]
        if time is not None:
            query = [
                {'declaretime': {'$regex': time}},
            ]
        data = col.aggregate(
            [
                # {
                #     '$match': query
                # },
                {
                    "$group": {
                        "_id":
                        {
                            'declaretime': '$declaretime',
                        }
                    }
                },
                {"$sort": {"_id.declaretime": 1}},
                # {"$skip": offset},
                # {"$limit": limit}
            ])
        data = [i['_id'] for i in data]
        return list(data)

    # elif data_type == 'city_statistic':
    #     pass
# %%


# class ModelName(str, Enum):
#     alexnet = "alexnet"
#     resnet = "resnet"
#     lenet = "lenet"


# @app.get("/models/{model_name}")
# async def get_model(model_name: ModelName):
#     if model_name == ModelName.alexnet:
#         return {"model_name": model_name.name, "message": "Deep Learning FTW!"}

#     if model_name.value == "lenet":
#         return {"model_name": model_name, "message": "LeCNN all the images"}

#     return {"model_name": model_name, "message": "Have some residuals"}
