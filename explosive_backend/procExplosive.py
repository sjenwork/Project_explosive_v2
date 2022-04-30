import pathlib
from textwrap import indent
from sqlalchemy import create_engine
import sqlalchemy
import copy
import geopandas as gpd
import re
import pandas as pd
from src.sql_tools import get_conn as connSQL, insert, table_check, fetchall
from src.mongo_tools import get_conn as connMongo
from src.tools import getFuncName
import json
import numpy as np
import os
from tqdm import tqdm
import datetime


pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.unicode.ambiguous_as_wide', True)


# 將原始檔案整理好後寫入資料庫
def data2sql_records():
    with open('data/explosiveapi2.json', 'r') as f:
        df = json.load(f)['records']
        for i, row in enumerate(df):
            if np.mod(i, 100) == 0:
                print(i)
            insert(row, 'explosive_records')


# 易爆物化學物質表
def data2sql_chemilist():
    with open('data/explosiveapi2.json', 'r') as f:
        df = json.load(f)['chemlist']
        for i, idf in enumerate(df):
            df[i]['chnname'] = df[i].pop('name')

        for i, row in enumerate(df):
            if np.mod(i, 100) == 0:
                print(i)
            insert(row, 'explosive_chemilist')


# 將原始資料寫入資料庫
def data2sql_rawdata():
    def colName():
        return [
            'DeclareTime',
            'DeptID',
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
            'DeclareDate',
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
        ]

    dftmp = []
    for i in [1, 4, 7, 10]:
        tmp = pd.read_excel(
            "/Volumes/GoogleDrive-114782082393599805732/我的雲端硬碟/Project_Frontend/A1_explosive/2022/dataProc/files/整併報表_2021年度整理檔.xlsx",
            sheet_name=f"整併報表{i:02d}",
            header=[0, 1]
        )
        tmp = tmp[tmp.isna().sum(axis=1) < 39]
        dftmp.append(tmp)
    df = pd.concat(dftmp)
    df_drop = [i for i in df.columns if 'combine' in i[1]]
    df = df.drop(df_drop, axis=1).iloc[:, :32]
    df.columns = colName()
    df.DeclareTime = df.DeclareTime.astype(int)
    df = df.drop('DeclareDate', axis=1)
    for col in df.columns:
        df[col] = df[col].astype(str)
    df = df.to_dict(orient='records')

    for i, row in enumerate(df):
        if np.mod(i, 100) == 0:
            print(i)
        insert(row, 'explosive_rawdata')


def write_tojson(data, name):
    with open(f'src/info/{name}.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def chemMapping2testdb():
    sql = '''SELECT * FROM [ChemiPrimary].[dbo].[ChemiMatchMapping]'''
    df = pd.read_sql(sql, con=connSQL('db_chemtest_ssh'))
    df.to_sql(
        'ChemiMatchMapping',
        con=connSQL('dbtest'),
        index=False,
        if_exists='append',
        dtype={
            'MatchNo': sqlalchemy.types.INT,
            'CASNoMatch': sqlalchemy.types.NVARCHAR,
            'ChemiChnNameMatch': sqlalchemy.types.NVARCHAR,
            'ChemiEngNameMatch': sqlalchemy.types.NVARCHAR,
            'ChemiChnAliases': sqlalchemy.types.NVARCHAR,
            'ChemiEngAliases': sqlalchemy.types.NVARCHAR,
            'CreateDate': sqlalchemy.types.DATETIME,
            'ModifyDate': sqlalchemy.types.DATETIME,
        }
    )


def save2jsonserver():
    con = connSQL('dbtest')
    chemilist = pd.read_sql('select * from dbo.explosive_chemilist', con=con)
    data_all = pd.read_sql('select * from dbo.explosive_records_all', con=con)
    data_fac = pd.read_sql('select * from dbo.explosive_records_fac', con=con)
    data_city = pd.read_sql(
        'select * from dbo.explosive_records_city', con=con)
    chemilist = chemilist.replace('', np.nan).replace(np.nan, None)
    data_all = data_all.replace('', np.nan).replace(np.nan, None)
    data_fac = data_fac.replace('', np.nan).replace(np.nan, None)
    data_city = data_city.replace('', np.nan).replace(np.nan, None)

    with open('jsonapi/explosive.json', 'w') as f:
        json.dump({
            'chemilist': chemilist.to_dict(orient='records'),
            'records_all': data_all.to_dict(orient='records'),
            'records_city': data_city.to_dict(orient='records'),
            'records_fac': data_fac.to_dict(orient='records'),
        }, f, ensure_ascii=False, indent=2)

# 以上為資料準備
# ------------------------------------------------------------
# 以下為易爆物資料整理至寫入資料庫
# 讀取指引表


def getChemMap_All(machineName):
    sql = 'SELECT * FROM ChemiMatchMapping'
    cols = ['MatchNo', 'CASNoMatch', 'ChemiChnNameMatch', 'ChemiEngNameMatch',
            'ChemiChnAliases', 'ChemiEngAliases']
    chemMap = pd.read_sql(sql, con=connSQL(
        machineName, name=getFuncName()))[cols]
    chemMap_e2n = chemMap.set_index('ChemiEngNameMatch')[
        'CASNoMatch']  # .str.lower()
    chemMap_e2n.index = chemMap_e2n.index.str.lower()
    chemMap_e2n = chemMap_e2n.to_dict()
    chemMap_n2e = chemMap.set_index('CASNoMatch')[
        'ChemiEngNameMatch']  # .str.lower()
    chemMap_n2e = chemMap_n2e.to_dict()
    return {'e2n': chemMap_e2n, 'n2e': chemMap_n2e}


def getChemMap_Explosive():
    pth = pathlib.Path(os.path.abspath('.'))
    with open(pth/'src/info/explosive_nameMap.json') as f:
        namemap = json.load(f)
    return namemap


def groupByFac(data, cols=[('ComFacBizName', ''), ('ComFacBizAddress', ''), ('import_info', 'X'), ('import_info', 'Y')]):
    def procColName(cols):
        return ['-'.join(i) if i[1] != '' else i[0] for i in cols]

    # data = copy.deepcopy(data)
    data.columns = procColName(data.columns)
    col_groupby = procColName(cols)
    # data = copy.deepcopy(p.df2)
    # col_merge = ['-'.join(i) if i[1] != '' else i[0] for i in data.columns]
    # col_groupby = ['-'.join(i) if i[1] != '' else i[0] for i in cols]
    # data.columns = col_merge
    forLoop = data[col_groupby].assign(
        group='').sort_values(by='ComFacBizName')
    groupingData = copy.deepcopy(forLoop)
    groupind = 0
    for i, row in tqdm(forLoop.iterrows(), desc='grouping factory', total=len(forLoop)):
        if groupingData.loc[i, 'group'] != '':
            continue
        ind0 = groupingData.group == ''
        data_source = forLoop.iloc[:, :3][ind0]  # 取出比較來源資料
        data_target = pd.concat(
            [row.iloc[:3].to_frame().T] * len(data_source)).reset_index(drop=True)  # 生成一個和比較來源一樣大小的df
        data_target.index = data_source.index
        ind = (data_source == data_target).sum(axis=1)
        ind2 = groupingData[ind0][ind > 0].index
        groupingData.loc[ind2, 'group'] = groupind
        groupind += 1
    # 處理群組間可能是相關的單位
    # tmp = groupingData.groupby('ComFacBizName').group.agg(
    #     lambda i: ','.join(map(str, set(i))))
    # tmp = tmp[tmp.str.contains(',')]
    groupingData.group = groupingData.group.apply(lambda i: f'h{i}')
    groupingData.index.name = 'index'
    groupingData = groupingData.reset_index()
    groupingData_grouped = (
        groupingData
        .groupby(['group', 'ComFacBizAddress', 'ComFacBizName', 'BusinessAdminNo'])
        .agg({'index': lambda i: ','.join(map(str, i))})
        .reset_index()
        .rename(columns={'index': 'indexList'})
    )

    grp2name = groupingData[['group', 'ComFacBizName']].groupby(['group']).agg(
        lambda i: i.iloc[0])
    grp2admino = groupingData[['group', 'BusinessAdminNo']].groupby(['group']).agg(
        lambda i: i.iloc[0])

    # groupingData['ComFacBizName_list'] = groupingData['group'].map(
    #     groupingData.groupby('group').ComFacBizName.agg(
    #         lambda i: (','.join(set(i))))
    # )
    # groupingData['BusinessAdminNo_list'] = groupingData['group'].map(
    #     groupingData.groupby('group').BusinessAdminNo.agg(
    #         lambda i: (','.join(map(str, set(i)))))
    # )
    groupingData['ComFacBizName_rep'] = groupingData['group'].map(
        grp2name.ComFacBizName)
    groupingData['BusinessAdminNo_rep'] = groupingData['group'].map(
        grp2admino.BusinessAdminNo)

    # data2 = pd.concat([data, groupingData['group']], axis=1)
    data2 = (
        data.drop(columns=[
            'ComFacBizName', 'BusinessAdminNo', 'ComFacBizAddress'])
        .merge(groupingData[['index', 'group', 'ComFacBizName_rep', 'BusinessAdminNo_rep']], left_index=True, right_on='index')
        .rename(columns={'ComFacBizName_rep': 'ComFacBizName', 'BusinessAdminNo_rep': 'BusinessAdminNo'})
    )
    # data2 = pd.concat([
    #     data.drop(columns=['ComFacBizName', 'BusinessAdminNo']),
    #     groupingData['ComFacBizName'], groupingData['BusinessAdminNo'], groupingData['group'],
    # ], axis=1)
    return data2, groupingData


def wide2long(data):
    data2 = {}
    for operation in ['import', 'produce', 'usage', 'storage']:
        cols1 = [
            'time', 'deptid', 'casno', 'RegionType',
            'ComFacBizName', 'BusinessAdminNo', 'group', 'index'
        ]
        cols2 = [f'{operation}_info-{i}' for i in ['Quantity', 'X', 'Y']]
        cols = cols1 + cols2
        data2[operation] = data[cols]

    # 相同「運作行為(operation)、區域類別(RegionType)、期別(time)、化學物質(casno)、
    # 來源(deptid)、廠商(ComFacBizName、BusinessAdminNo、group)、座標(X、Y)」的資料加總
    data3 = copy.deepcopy(data2)
    for key in data2.keys():
        colname = f'{key}_info-Quantity'
        item = data2[key].astype({colname: float, 'index': str})
        item = item[item[colname] > 0]
        aggfun = {
            colname: 'sum',
            'index': lambda i: ','.join(i),
        }
        item_1 = (
            item[item[f'{key}_info-X'] != '-']
            .assign(count=0)
            .groupby([
                'group', 'ComFacBizName', 'BusinessAdminNo', 'casno', 'time', 'deptid', 'RegionType',
                f'{key}_info-X', f'{key}_info-Y'])
            .agg(aggfun)
        )
        item_2 = (
            item[item[f'{key}_info-X'] == '-']
            .set_index([
                'group', 'ComFacBizName', 'BusinessAdminNo', 'casno', 'time', 'deptid', 'RegionType',
                f'{key}_info-X', f'{key}_info-Y'], drop=True)
        )

        data3[key] = (
            pd.concat([item_1, item_2])
            .sort_index()
            .rename({f'{key}_info-Quantity': 'Quantity'}, axis=1)
            .rename_axis(
                index=lambda i: i.replace(f'{key}_info-', ''))
        )
    data4 = pd.concat(data3).rename_axis(
        index={None: 'operation'}).reset_index()
    data4['name'] = data4['casno'].map(getChemMap_Explosive())
    return data4


def getLatest(data):
    data['time_latest'] = (data.groupby(
        ['operation', 'group',  'casno', 'deptid', 'RegionType', 'lon', 'lat'])
        .time.transform(max)
    )
    return data


def locateCounty(data):
    data.loc[data[data.X == '-'].index, 'X'] = None
    data.loc[data[data.Y == '-'].index, 'Y'] = None
    # 二度分帶 to WGS
    data2 = gpd.GeoDataFrame(
        data, geometry=gpd.points_from_xy(data['X'], data['Y'], crs='epsg:3826'))
    data2 = data2.to_crs('epsg:4326')
    data2['lon'] = data2.geometry.apply(
        lambda i: i.x if not i.is_empty else '')
    data2['lat'] = data2.geometry.apply(
        lambda i: i.y if not i.is_empty else '')

    # 行政區定位
    taiwan = gpd.read_file('src/info/county.json')
    taiwan = taiwan.set_index("COUNTYNAME")['geometry']
    geometry = data2[['geometry']]
    pnts = geometry.assign(**{key: geometry.within(geom)
                              for key, geom in taiwan.items()})
    q = pnts.iloc[:, 1:].replace(
        False, np.nan).stack().reset_index().iloc[:, :2].set_axis(['index', 'city'], axis=1).set_index('index')
    data3 = data2.merge(q, left_index=True, right_index=True, how='left')
    data3.city = data3.city.fillna('')
    data4 = pd.DataFrame(data3.drop(columns=['geometry']))
    data4.time = data4.time.astype(int)
    return data4


def statisticByCity(data):
    data2 = data.groupby(['time', 'operation', 'name', 'casno', 'city'])[
        'Quantity'].sum().reset_index()
    return data2


def statisticByFac(data):
    # 群組相同，但廠商名稱、統編、座標不同的，會被拆分成多個項目（給繪製地圖用，不同座標可標示在不同座標）
    # 不同來源須分開
    # 另須移除沒有座標的

    data2 = data.groupby([
        "time", "operation", "name", "casno", "lon", "lat", "group", "ComFacBizName", "BusinessAdminNo", 'deptid', 'RegionType'
    ]
    ).agg({
        'Quantity': 'sum',
        'index': ','.join
    }).reset_index()
    data2 = data2[data2.lon != '']
    return data2


def statisticByFac_forTable(data):
    # 依據群組與來源做整合，只要群組相同，就整合在一起，若是有多個廠商、多個座標、多個來源、多個統編，會條列式
    # 給表格用
    data2 = data.groupby([
        "time", "operation", "name",  "group", "deptid"]
    ).agg({
        'Quantity': 'sum',
        'ComFacBizName': lambda i: ','.join(set(i)),
        'BusinessAdminNo': lambda i: ','.join(set(i)),
        'ComFacBizName_list': lambda i: ','.join(set(i)),
        'BusinessAdminNo_list': lambda i: ','.join(set(i)),
        'lon': lambda i: ','.join(map(str, set(i))),
        'lat': lambda i: ','.join(map(str, set(i))),
        'index': lambda i: ','.join(i)
    }).reset_index()
    return data2


def handleProcRecord(method, nlen=None):
    import datetime
    now = datetime.datetime.now()
    db = connMongo(machineName)
    col = db['status']
    if method == 'save':
        if 'status' not in db.list_collection_names():
            col.insert_one(
                {"name": "history", "count": nlen, "updatetime": now})
        else:
            col.update_one({"name": "history"}, {
                "$set": {"count": nlen, "updatetime": now}})
    elif method == 'load':
        nlen = col.find_one({"name": 'history'})['count']
        return nlen


class proc_explosive_chem():
    def desc(self):
        print('''
        df1: 原始資料（篩選過欄位）
        df2: 移除casno == ''
        ''')

    def __init__(self, machineName, method='overwrite'):
        self.method = method
        self._getChemMap(machineName)
        self._getExplosiveData(machineName)
        self.procChemName(copy.deepcopy(self.df.chem))
        # self.df3 = groupByFac(self.df2)
        # self.df4 = wide2long(self.df3)
        # self.df5 = locateCounty(self.df4)

    def _getChemMap(self, machineName):
        self.chemMapAll = getChemMap_All(machineName)
        self.chemMapExplosive = getChemMap_Explosive()

    def _getExplosiveData(self, machineName):
        sql = 'SELECT * FROM ChemiPrimary.dbo.ExplosiveMergeData'
        if self.method == 'append':
            sql += ' where isProc=0'
        df = pd.read_sql(sql, con=connSQL(machineName, name=getFuncName()))

        # df = df.drop([
        #     'FCOUNTY', 'FTOWN', 'FCOUNTY_TOWN', 'CountyTownship', 'UpdateDate',
        #     'IsMerge', 'ProductionZipCode', 'UseageZipCode', 'StorageZipCode'], axis=1)

        pth = pathlib.Path(os.path.abspath('.'))
        with open(pth/'src/info/explosive_columns.json') as f:
            cols = json.load(f)

        df = df[cols['used']]
        df.columns = pd.MultiIndex.from_tuples(cols['nameMap'])
        # 將所有運作量為0的移除
        Quantity_col = [i for i in df.columns if i[1] == 'Quantity']
        df = df.astype(dict(zip(Quantity_col, [float]*4)))
        df = df[df[Quantity_col].sum(axis=1) > 0]
        # 將統編格式統一
        df.BusinessAdminNo = df.BusinessAdminNo.apply(lambda i: i.zfill(8))

        self.df = df

    def procChemName(self, chem):
        # 整理casno，將不在列表內的物質移除
        cas2nameAlle2n = self.chemMapAll['e2n']
        cas2nameExp = self.chemMapExplosive
        chem.cname = chem.cname.map(cas2nameExp).map(cas2nameExp)
        chem.casno = chem.casno.map(cas2nameExp).map(cas2nameExp)
        chem.ename = chem.ename.str.lower().map(
            cas2nameAlle2n).map(cas2nameExp)  # .map(cas2nameExp)
        chem['cn2cas'] = chem.cname.map(cas2nameExp)
        chem['en2cas'] = chem.ename.str.lower().map(cas2nameExp)
        chem['cas2cn'] = chem.casno.map(cas2nameExp)
        chem = chem.fillna('')

        # 將沒有casno的物質以中英文名取代
        chem.loc[chem[chem.casno == ''].index,
                 'casno'] = chem.loc[chem[chem.casno == ''].index, 'cn2cas']
        chem.loc[chem[chem.casno == ''].index,
                 'casno'] = chem.loc[chem[chem.casno == ''].index, 'en2cas']
        chem = chem[['casno']]
        chem.columns = pd.MultiIndex.from_tuples([('casno', '')])
        self.chem = chem

        self.df = self.df.drop('chem', axis=1, level=0).merge(
            chem, left_index=True, right_index=True)
        self.df2 = self.df.drop(self.df[self.df.casno == ''].index)


def saveRecords(data, colname, machineName, method):
    db = connMongo(machineName)
    col = db[colname]
    if method == 'overwrite':
        col.delete_many({'databaseName': 'explosive'})
    col.insert_many(data)


def getFacList(data):
    # data = copy.deepcopy(data)[['ComFacBizName', 'BusinessAdminNo', 'group']]
    data = data.drop(columns=['index', 'ComFacBizName_rep', 'BusinessAdminNo_rep']).drop_duplicates(
        subset=['ComFacBizName', 'BusinessAdminNo', 'group'])
    data['label'] = data['BusinessAdminNo'] + ' ' + data['ComFacBizName']
    return data


def getTimeList(df5):
    timeList = (
        pd.DataFrame(
            copy.deepcopy(df5).time.unique(), columns=['time']
        ).astype({'time': str})
        .sort_values(by='time')
        .reset_index(drop=True)
    ).reset_index()
    timeList['timeString'] = (
        timeList['time']
        .str.replace('01$', 'Q1', regex=True)
        .str.replace('04$', 'Q2', regex=True)
        .str.replace('07$', 'Q3', regex=True)
        .str.replace('10$', 'Q4', regex=True)
    )
    timeList['label'] = (
        timeList['timeString']
        .str.replace('Q1', ' 第一季', regex=True)
        .str.replace('Q2', ' 第二季', regex=True)
        .str.replace('Q3', ' 第三季', regex=True)
        .str.replace('Q4', ' 第四季', regex=True)
    )
    timeList = pd.concat(
        [timeList,
         pd.DataFrame([[timeList['index'].max()+1, '最新申報', 'latest', '最新申報']], columns=timeList.columns)]
    )
    return timeList  # .to_dict(orient='records')


def df2record(data):
    now = datetime.datetime.now()
    return (
        data
        .fillna('-')
        .replace('', '-')
        .assign(updatetime=now)
        .assign(databaseName='explosive')
        .to_dict(orient='records')
    )


def getChemList(data):
    data = data[['name', 'casno']].drop_duplicates().reset_index(drop=True)
    data['label'] = data['name'] + ' ' + data['casno']
    data = data.rename(columns={'name': 'chnname'})
    return data


if __name__ == '__main__':
    test = False
    save = True
    load = False

    save_paras = {
        'method': 'overwrite',
        'machineName': 'mongo_chemtest_outside_container'
    }
    method = 'overwrite'
    if not test:
        machineName = 'mssql_chemtest'
        p = proc_explosive_chem(machineName, method=method)
        df3, groupingData = groupByFac(p.df2, cols=[
            ('ComFacBizName', ''),
            ('ComFacBizAddress', ''),
            ("BusinessAdminNo", ''),
        ])  # 以廠商名稱、地址、統一編號
        df4 = wide2long(df3)  # 資料統整
        df5 = locateCounty(df4)  # 座標轉換與定位
        df5 = getLatest(df5)  # 取得各公司最新的時間點
        df6 = statisticByCity(df5)

        # df7 = statisticByFac(df5)
        # df8 = statisticByFac_forTable(df5)
        df9 = getFacList(groupingData)
        df10 = getTimeList(df5)
        df11 = getChemList(df5)

        saveRecords(df2record(groupingData),
                    colname='group2ComFacBizMapping', **save_paras)
        saveRecords(df2record(df5),
                    colname='ComFacBizHistory_allStatistic', **save_paras)
        # saveRecords(df2record(df6),
        #             colname='ComFacBizHistory_cityStatistic', **save_paras)
        saveRecords(df2record(df9),
                    colname='ComFacBizList', **save_paras)
        saveRecords(df2record(df10),
                    colname='timeList', **save_paras)
        saveRecords(df2record(df11),
                    colname='chemList', **save_paras)

        # test
        if False:
            df_test = copy.deepcopy(df11)
            saveRecords(df2record(df_test),
                        colname='chem_test', **save_paras)

            db = connMongo('mongo_chemtest_outside_container', 'explosive')
            db['chem_test'].delete_many({'databaseName': 'explosive'})
