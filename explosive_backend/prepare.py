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

# from tabulate import tabulate


def print2(message, path='rel'):
    caller = getframeinfo(stack()[1][0])
    # python3 syntax print
    # print("%s:%d - %s" % (caller.filename, caller.lineno, message))
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

app = FastAPI(openapi_tags=tags_metadata)

pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.unicode.ambiguous_as_wide', True)
# sheets = pd.ExcelFile('rawdata/高風險化學品2次上傳彙整.xlsx')
# df = pd.read_excel("歷年國內主要觀光遊憩據點遊客人數月別統計.xlsx", sheet_name=None)

cols_raw = [
    'CASNo',
    'ChemicalChnName',
    'ChemicalEngName',
    'SourceDept',
    'ResponsibleName',
    'ResponsibleTel',
    'ResponsiblePhone',
    'EmergencyName',
    'EmergencyTel',
    'EmergencyPhone',
    'ComFacBizName',
    'BusinessAdminNo',
    'FactoryRegNo',
    'ComFacBizAddress',
    'PlaceType',
    'RegionType',
    'RegionName',
    'ComFacBizTWD97X',
    'ComFacBizTWD97Y',
    'DeclareTime',
    'ImportQuantity',
    'ProductionQuantity',
    'ProductionTWD97X',
    'ProductionTWD97Y',
    'UseageQuantity',
    'UseageTWD97X',
    'UseageTWD97Y',
    'StorageQuantity',
    'StorageTWD97X',
    'StorageTWD97Y',

    # 'DeptID',
    # 'DeclareDate',
]

cols = [
    'casno',
    'cname',
    'ename',
    'srcdept',
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
    'regionNname',
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
    'checkAdmin',
    'checktime'
    # 'DeptID',化學物質中文名
    # 'DeclareDate',
]

col_map = {
    'casno': 'CAS No.',
    'cname': '化學物質中文名',
    'ename': '化學物質英文名',
    'srcdept': '資料來源',
    'resname': '聯絡資料：公司負責人',
    'restel': '聯絡資料：聯絡電話',
    'resphone': '聯絡資料：手機號碼',
    'emername': '聯絡資料：緊急連絡人',
    'emertel': '聯絡資料：緊急連絡人電話',
    'emerphone': '聯絡資料：緊急連絡人手機',
    'comname': '廠商基本資料：公司/工廠名稱',
    'adminno': '廠商基本資料：統一編號(8碼)',
    'regno': '廠商基本資料：工廠登記證號',
    'addr': '廠商基本資料：地址',
    'placetype': '廠商基本資料：運作場所型態備註(工廠/倉庫)',
    'regiontype': '廠商基本資料：廠商所在區域類別(科學園區/工業區/加工出口區/港區/其他)',
    'regionNname': '廠商基本資料：廠商所在區域名稱(科學園區/工業區/加工出口區/港區/其他)',
    'importX': '廠商地址座標資訊 TWD97_X',
    'importY': '廠商地址座標資訊 TWD97_Y',
    'declaretime': '申報年月',
    'importQ': '輸入量',
    'prodQ': '製造量',
    'prodX': '製造地點座標資訊TWD97_X',
    'prodY': '製造地點座標資訊TWD97_Y',
    'usageQ': '使用量',
    'usageX': '使用地點座標資訊TWD97_X',
    'usageY': '使用地點座標資訊TWD97_Y',
    'storageQ': '貯存量',
    'storageX': '貯存地點座標資訊TWD97_X',
    'storageY': '貯存地點座標資訊TWD97_Y',
    'checkAdmin': '查核機關',
    'checktime': '查核時間',
    # 'DeptID',
    # 'DeclareDate',
}


preparing = False
running = True

if preparing:
    def read_excel(sn):
        data = pd.read_excel('rawdata/高風險化學品2次上傳彙整.xlsx',
                             sheet_name=sn, header=[0, 1], converters={('廠商基本資料', '統一編號(8碼)'): str, ('廠商基本資料', '工廠登記證號'): str})
        data.columns = cols
        data['DeclareDate'] = re.sub(r"[\u4e00-\u9fff]+", '', sn).strip()
        print(sn, data.shape)
        return data
    # %%
    sheets = pd.ExcelFile('rawdata/高風險化學品2次上傳彙整.xlsx').sheet_names

    dfs = list(map(read_excel, sheets[:]))
    df = pd.concat(dfs).astype(object)
    df = df.where(pd.notnull(df), None)
    df = df.replace('-', None)
    # df = df.drop(columns=[
    #     'resname', 'restel', 'resphone', 'emername', 'emertel', 'emerphone',
    #     'placetype', 'regionNname',
    # ])
    df.importQ = df.importQ.fillna(0)
    df.prodQ = df.prodQ.fillna(0)
    df.usageQ = df.usageQ.fillna(0)
    df.storageQ = df.storageQ.fillna(0)

    for operation in ['import', 'prod', 'usage', 'storage']:
        data = gpd.GeoDataFrame(
            df[[f'{operation}X', f'{operation}Y']],
            geometry=gpd.points_from_xy(
                df[f'{operation}X'], df[f'{operation}Y'], crs='epsg:3826')
        )
        data = data.to_crs('epsg:4326')
        df[f'{operation}X2'] = data.geometry.apply(
            lambda i: i.x if not i.is_empty else '')
        df[f'{operation}Y2'] = data.geometry.apply(
            lambda i: i.y if not i.is_empty else '')
    df['id'] = list(range(len(df)))
    df = df.reset_index(drop=True)

    # df = df.to_dict(orient='records')

    df2 = copy.deepcopy(df)
    # %%
    # 處理廠商整合
    df2['comname_merged'] = ''
    df2['addr_merged'] = ''
    for irow, row in tqdm(df.iterrows(), desc='grouping factory', total=len(df)):
        # for irow, row in df.iterrows():
        # if irow > 10:
        #     continue
        if df2.loc[irow, 'comname_merged'] != '':
            continue
        name = row['comname']
        addr = row['addr']
        ind = df[(df.addr == addr) | (df.comname == name)].index

        # comname_merged = df2.loc[ind]
        # comname_merged = comname_merged.apply(
        #     lambda i: name if i['comname_merged'] == name else f"{name}({i['comname_merged']})", axis=1)
        # df2.loc[ind, 'comname_merged'] = comname_merged.tolist()

        # addr_merged = df2.loc[ind]
        # addr_merged = addr_merged.apply(
        #     lambda i: name if i['addr_merged'] == name else f"{name}({i['addr_merged']})", axis=1)
        # df2.loc[ind, 'addr_merged'] = addr_merged.tolist()
        namelist = ','.join(list(set(df2.loc[ind, 'comname'].tolist())))
        df2.loc[ind, 'comname_merged'] = namelist
        addrlist = ','.join(list(set(df2.loc[ind, 'addr'].tolist())))
        df2.loc[ind, 'addr_merged'] = addrlist
        # print(irow)

    # %%
    # 處理化學物質整合
    df2['chem_merged'] = ''
    for irow, row in tqdm(df.iterrows(), desc='grouping chem', total=len(df)):
        if df2.loc[irow, 'chem_merged'] != '':
            continue
        casno = row.casno
        cname = row.cname
        ename = row.ename
        ind = df[(df.casno == casno) | (df.cname == cname)
                 | (df.ename == ename)].index

        chemlist = ','.join(list(set(df2.loc[ind, 'casno'].tolist())))
        df2.loc[ind, 'chem_merged'] = chemlist

    # %%
    # 取得化學物質列表
    # sel_col_chem = ['casno', 'cname', 'ename', 'chem_merged']
    # chemical_list = df2[sel_col_chem].drop_duplicates(subset=sel_col_chem[:-1])

    # %%
    # 取得廠商列表
    # sel_col_com = ['comname', 'adminno', 'regno', 'comname_merged']
    # company_list = df2[sel_col_com].drop_duplicates(subset=sel_col_com[:-1])

    # %%

    df3 = df2.to_dict(orient='records')
    # chemical_list = chemical_list.to_dict(orient='records')
    # company_list = company_list.to_dict(orient='records')

    writingdb = True
    # 寫入資料庫
    if writingdb:
        client = MongoClient(f"mongodb://localhost:27017/",
                             serverSelectionTimeoutMS=5)
        db = client['explosive']
        # 寫資料
        col = db.mergedRecords
        try:
            col.create_index('id', unique=True)
        except:
            pass
        res = col.bulk_write(
            [UpdateOne({'id': i['id']}, {"$set": i}, upsert=True)
             for i in df3]
        )
        # 寫化學物質列表
        # col = db.chemical_list
        # res = col.bulk_write(
        #     [UpdateOne({'cname': i['cname'], 'ename': i['ename'], 'casno': i['casno'], }, {"$set": i}, upsert=True)
        #      for i in chemical_list]
        # )
        # 寫廠商列表
        # col = db.company_list
        # res = col.bulk_write(
        #     [UpdateOne({'comname': i['comname'], 'adminno': i['adminno'], 'regno': i['regno'], }, {"$set": i}, upsert=True)
        #      for i in company_list]
        # )


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


class operationModel(str, Enum):
    usage = 'usage'
    storage = 'storage'
    prod = 'prod'
    importing = 'import'


if running:
    @app.get("/explosiveapi_ver3/{data_source}", tags=['易爆物與高風險化學物質 ver3'])
    def datalist(
        data_source: sourceModel,
        company_name: str = None,
        chemical_name: str = None,
        operation: operationModel = None,
        offset: int = 0,
        limit: int = 20,
        display: bool = True,
    ):

        client = MongoClient(f"mongodb://localhost:27017/",
                             serverSelectionTimeoutMS=5)
        db = client['explosive']
        col = db[data_source]

        if data_source == 'mergedRecords':
            query = {}
            constraint = {'_id': 0}

            if chemical_name is not None:
                query = (query | {'chem_merged': {'$regex': chemical_name}})

            if display:
                # 網頁呈現
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
                        # 'comname_merged': 0,
                        # 'chem_merged': 0,
                        'declaretime': 0,
                    }
                )
                # .skip(offset).limit(limit)
                data = col.find(query, constraint)
                data = list(data)

                data2 = pd.DataFrame.from_records(data)
                if operation is not None:
                    stat_cols = ['comname', 'addr', 'adminno', 'regno', 'casno',
                                 'cname', 'ename', 'checkAdmin', 'checktime', 'DeclareDate',
                                 'comname_merged', 'chem_merged',
                                 'regiontype', 'srcdept'] + [f"{operation}Q", f"{operation}X2", f"{operation}Y2", ]
                    data2 = data2[stat_cols]
                    # print(data2['regno'].dtype)
                    data2 = data2.fillna('-')
                    data2 = (
                        data2
                        .groupby(
                            [
                                'DeclareDate', 'srcdept', 'comname_merged', 'regiontype', 'cname',
                                f"{operation}X2", f"{operation}Y2",
                            ], as_index=False
                        )
                        .agg(
                            {
                                f"{operation}Q": sum,
                                "adminno": ','.join,
                                "regno": ','.join,
                                "addr": ','.join,
                                "cname": lambda i: i.iloc[0],
                                "ename": lambda i: i.iloc[0],
                                "casno": lambda i: i.iloc[0]

                            }
                        )
                    )
                # data2.to_excel('test.xlsx')
                # print(data2)
                return HTMLResponse(content=data2.to_html(), status_code=200)

                return data2.to_html()
                return data2.to_dict(orient='records')
            else:
                # 資料下載（原始資料）
                constraint = {
                    '_id': 0
                }
                # .skip(offset).limit(limit)
                data = list(col.find(query, constraint))
                data2 = pd.DataFrame.from_records(
                    data)[cols].rename(columns=col_map)
                # print(data2)
                # return data2.to_markdown()
                return data2.to_dict(orient='records')

        elif data_source == 'chemical_list':
            query = {}
            if chemical_name is not None:
                query = (
                    query |
                    {
                        '$or':
                        [
                            {'cname': {'$regex': chemical_name}},
                            {'ename': {'$regex': chemical_name}},
                            {'casno': {'$regex': chemical_name}},
                        ]
                    }
                )

            data = col.find(query, {'_id': 0}).skip(offset).limit(limit)
            return list(data)

        elif data_source == 'company_list':
            query = {}
            if company_name is not None:
                query = (
                    query |
                    {'$or':
                     [
                         {'comname': {'$regex': company_name}},
                         {'regno': {'$regex': company_name}},
                         {'adminno': {'$regex': company_name}},
                     ]
                     }
                )

            data = col.find(query, {'_id': 0}).skip(offset).limit(limit)
            return list(data)

        query = {}

        # data = list(col.find(query, {'_id': False}))
        # print(data)
        # print(len(data))

        return data

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
    ):

        client = MongoClient(f"mongodb://localhost:27017/",
                             serverSelectionTimeoutMS=5)
        db = client['explosive']
        col = db[data_source]

        if data_type == 'data_list':
            query = {}
            query_time = {'DeclareDate': {}}
            constraint = {'_id': 0}

            if chemical_name is not None:
                query = (query | {'chem_merged': {'$regex': chemical_name}})

            if company_name is not None:
                query = (query | {'comname_merged': {'$regex': company_name}})

            if not time_latest:
                if time is not None:
                    query_time['DeclareDate'] = time
                if time_ge is not None:
                    query_time['DeclareDate']['$gte'] = time_ge
                if time_le is not None:
                    query_time['DeclareDate']['$lte'] = time_le
                if query_time['DeclareDate'] != {}:
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
                        # 'comname_merged': 0,
                        # 'chem_merged': 0,
                        'declaretime': 0,
                    }
                )
                data = col.find(query, constraint)
                data = list(data)

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
                        'cname', 'ename', 'checkAdmin', 'checktime', 'DeclareDate',
                        'comname_merged', 'chem_merged',
                        'regiontype', 'srcdept'
                    ] + [
                        f"{operation}Q",
                        f"{operation}X2",
                        f"{operation}Y2",
                    ]
                    data2 = data2[stat_cols]
                    data2 = data2.fillna('-')

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
                                        'srcdept', 'comname_merged', 'regiontype', 'cname',
                                        f"{operation}X2", f"{operation}Y2",
                                    ], as_index=False
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
                                        "DeclareDate": lambda i: f"{time_ge if time_ge else '_'} -> {time_le if time_le else '_'}",
                                        "checkAdmin": lambda i: ','.join(set(i)),
                                        "checktime": lambda i: ','.join(set(i)),
                                        "chem_merged": lambda i: ','.join(set(i)),
                                    }
                                )
                                .assign(operation=operation.name)
                                .rename(columns={
                                    f'{operation}X2': 'X',
                                    f'{operation}Y2': 'Y',
                                    f'{operation}Q': 'Q',
                                })
                            )
                            print2(
                                f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['DeclareDate']} }} 查詢")
                            print2(f"統計後共 {len(data2)} 筆")
                            print()
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
                                        'srcdept', 'comname_merged', 'regiontype', 'cname',
                                        f"{operation}X2", f"{operation}Y2",
                                    ]
                                )[f"{operation}Q"]
                                .transform(max)
                                ==
                                data2[f"{operation}Q"]
                            )
                            data2 = data2[idx]
                            print2('選擇較最大的')
                            print2(
                                f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['DeclareDate']} }} 查詢")
                            print2(f"統計後共 {len(data2)} 筆")
                            print()
                            # -> 若運作量相同，選擇較新的
                            idx = (
                                data2
                                .groupby(
                                    [
                                        'srcdept', 'comname_merged', 'regiontype', 'cname',
                                        f"{operation}X2", f"{operation}Y2",
                                    ]
                                )["DeclareDate"]
                                .transform(max)
                                ==
                                data2["DeclareDate"]
                            )
                            data2 = data2[idx]
                            print2('選擇較較新的')
                            print2(
                                f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['DeclareDate']} }} 查詢")
                            print2(f"統計後共 {len(data2)} 筆")
                            print()
                            # -> 若還有同期別，則進行加總

                            data2 = (
                                data2
                                .groupby(
                                    [
                                        'srcdept', 'comname_merged', 'regiontype', 'cname',
                                        f"{operation}X2", f"{operation}Y2",
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
                                        "DeclareDate": lambda i: f"{time_ge if time_ge else '_'} -> {time_le if time_le else '_'}",
                                        "checkAdmin": lambda i: ','.join(set(i)),
                                        "checktime": lambda i: ','.join(set(i)),
                                        "chem_merged": lambda i: ','.join(set(i)),
                                    }
                                )

                            )

                            data2 = (
                                data2
                                .reset_index(drop=True)
                                .assign(operation=operation.name)
                                .rename(columns={
                                    f'{operation}X2': 'X',
                                    f'{operation}Y2': 'Y',
                                    f'{operation}Q': 'Q',
                                })
                            )
                            print2(
                                f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['DeclareDate']} }} 查詢")
                            print2(f"統計後共 {len(data2)} 筆")
                            print()
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
                                    'srcdept', 'comname_merged', 'regiontype', 'cname',
                                ]
                            )[f"DeclareDate"]
                            .transform(max)
                            ==
                            data2["DeclareDate"]
                        )
                        data2 = (
                            data2[idx]
                            .assign(operation=operation.name)
                            .reset_index(drop=True)
                            .rename(columns={
                                f'{operation}X2': 'X',
                                f'{operation}Y2': 'Y',
                                f'{operation}Q': 'Q',
                            })
                        )
                        # return {'status': '查詢最新運作量'}
                        print2(
                            f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: latest }} 查詢")
                        print2(f"統計後共 {len(data2)} 筆")
                        print()

                    data2 = data2[[
                        'DeclareDate', 'srcdept', 'comname_merged', 'comname', 'regiontype', 'addr', 'adminno', 'regno',
                        'cname', 'ename', 'casno', 'chem_merged',
                        'operation', 'X', 'Y',  "Q",
                        'checkAdmin', 'checktime'
                    ]]
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
                            'DeclareDate', 'srcdept', 'comname_merged', 'comname', 'regiontype', 'addr', 'adminno', 'regno',
                            'cname', 'ename', 'casno', 'chem_merged', 'checkAdmin', 'checktime'
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
                                ]
                            ].rename(
                                columns={
                                    f'{ioperation}X2': 'X',
                                    f'{ioperation}Y2': 'Y',
                                    f'{ioperation}Q': 'Q'}
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
                                    ['srcdept', 'cname', 'comname',
                                        'regiontype', 'operation']
                                )['Q'].transform(max) == data2_storage.Q
                            )
                            data2_storage = data2_storage[idx]

                            #  --> 貯存量相同，時間從新
                            idx = (
                                data2_storage
                                .groupby(
                                    ['srcdept', 'cname', 'comname',
                                        'regiontype', 'operation']
                                )['DeclareDate'].transform(max) == data2_storage.DeclareDate
                            )
                            data2_storage = data2_storage[idx]

                        #
                        # ['DeclareDate', 'srcdept', 'comname_merged', 'comname', 'regiontype',
                        # 'addr', 'adminno', 'regno', 'cname', 'ename', 'casno', 'chem_merged',
                        # 'checkAdmin', 'checktime', 'X', 'Y', 'Q', 'operation']
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
                                    ['srcdept', 'cname', 'comname',
                                        'regiontype', 'operation',
                                        'X', 'Y'],
                                    as_index=False
                                ).agg({
                                    "Q": sum,
                                    "adminno": lambda i: ','.join(set(i)),
                                    "comname_merged": lambda i: ','.join(set(i)),
                                    "regno": lambda i: ','.join(set(i)),
                                    "addr": lambda i: ','.join(set(i)),
                                    "comname": lambda i: i.iloc[0],
                                    "cname": lambda i: i.iloc[0],
                                    "ename": lambda i: i.iloc[0],
                                    "casno": lambda i: i.iloc[0],
                                    "DeclareDate": lambda i: f"{time_ge if time_ge else '_'} -> {time_le if time_le else '_'}",
                                    "checkAdmin": lambda i: ','.join(set(i)),
                                    "checktime": lambda i: ','.join(set(i)),
                                    "chem_merged": lambda i: ','.join(set(i)),
                                    "operation": lambda i: ','.join(set(i)),
                                })
                            )
                        #  ---------------------------------------------------------------------------------------

                        data2 = pd.concat([data2_storage, data2_others])
                        data2 = data2.fillna('-').reset_index(drop=True)

                        # print(data2)
                        print2(
                            f"化學物質查詢廠商 -> {{ chem: {chemical_name}, operation: {operation}, time: {query_time['DeclareDate']} }} 查詢")
                        print2(f"統計後共 {len(data2)} 筆")
                        print()
                    #  廠商查詢運作化學物質 -> 查詢期別區間 end
                    #  -------------------------------------------------------------------------------------------

                    #  -------------------------------------------------------------------------------------------
                    #  廠商查詢運作化學物質 -> 查詢最新期別
                    else:
                        # return {'status': '查詢廠商最新運作量'}
                        idx = (
                            data2
                            .groupby(
                                [
                                    'srcdept', 'comname_merged', 'regiontype', 'cname',
                                ]
                            )[f"DeclareDate"]
                            .transform(max)
                            ==
                            data2["DeclareDate"]
                        )
                        data2 = data2[idx].reset_index(drop=True)
                        data2 = data2.set_index([
                            'DeclareDate', 'srcdept', 'comname_merged', 'comname', 'regiontype', 'addr', 'adminno', 'regno',
                            'cname', 'ename', 'casno', 'chem_merged', 'checkAdmin', 'checktime'
                        ])
                        data3 = []
                        for ioperation in ['storage', 'usage', 'prod', 'import']:
                            tmp = data2[
                                [
                                    f'{ioperation}X2',
                                    f'{ioperation}Y2',
                                    f'{ioperation}Q',
                                ]
                            ].rename(
                                columns={
                                    f'{ioperation}X2': 'X',
                                    f'{ioperation}Y2': 'Y',
                                    f'{ioperation}Q': 'Q'}
                            ).assign(
                                operation=ioperation,
                            )

                            data3.append(tmp)
                        data2 = pd.concat(data3).reset_index()
                        data2 = data2[data2['Q'] > 0]
                        data2 = data2.fillna('-').reset_index(drop=True)

                        print2(
                            f"廠商查詢運作化學物質 -> {{ chem: {chemical_name}, operation: {operation}, time: latest }} 查詢")
                        print2(f"統計後共 {len(data2)} 筆")
                        print()
                        # return {}
                    #  廠商查詢運作化學物質 -> 查詢最新期別 end
                    #  -------------------------------------------------------------------------------------------
                    data2 = data2[[
                        'DeclareDate', 'srcdept', 'comname_merged', 'comname', 'regiontype', 'addr', 'adminno', 'regno',
                        'cname', 'ename', 'casno', 'chem_merged',
                        'operation', 'X', 'Y', "Q",
                        'checkAdmin', 'checktime',
                    ]]
                    data2 = data2.astype(object)
                    data2 = data2.where(pd.notnull(data2), None)
                    # data2[data2.isna] = None

                return HTMLResponse(content=data2.to_html(), status_code=200)
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
                    .from_records(data)[cols]
                    .rename(columns=col_map)
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
                    {'DeclareDate': {'$regex': time}},
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
                                'DeclareDate': '$DeclareDate',
                            }
                        }
                    },
                    {"$sort": {"_id.DeclareDate": 1}},
                    # {"$skip": offset},
                    # {"$limit": limit}
                ])
            data = [i['_id'] for i in data]
            return list(data)

# %%

    class ModelName(str, Enum):
        alexnet = "alexnet"
        resnet = "resnet"
        lenet = "lenet"

    @app.get("/models/{model_name}")
    async def get_model(model_name: ModelName):
        if model_name == ModelName.alexnet:
            return {"model_name": model_name.name, "message": "Deep Learning FTW!"}

        if model_name.value == "lenet":
            return {"model_name": model_name, "message": "LeCNN all the images"}

        return {"model_name": model_name, "message": "Have some residuals"}
