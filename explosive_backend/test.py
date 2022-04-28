import pandas as pd
from src.mongo_tools import get_conn as connMongo
import copy
machineName = 'mongo_chemtest_outside_container'
db = connMongo(machineName)
res = db.ComFacBizHistory_allStatistic.find({
    'time': {
        '$gte': 202010,
        '$lte': 202104
    },
    'name': "硝酸銨",
},
    {'_id': False, 'updatetime': False}
)


# res = db.ComFacBizHistory_allStatistic.find(
#     {
#         'time': {'$gte': 202010},
#         'time': {'$lte': 202104},
#         'name': "硝酸銨",
#         # 'operation': "storage"

#     },
#     {'_id': False, 'updatetime': False}
# )

data = pd.DataFrame.from_records(res)
data2 = data.groupby(['operation', 'city', 'casno',
                     'name'], as_index=False).agg({'Quantity': sum})
print(data2)


# groupby_col = list(data.columns.drop([
#     'time', 'Quantity', 'index', 'city', 'time_latest']))

# storage = copy.deepcopy(data.loc[data.operation == 'storage'])
# storage = (
#     (storage.sort_values(by='Quantity', ascending=False))
#     .groupby(groupby_col, as_index=False)
#     .agg({'Quantity': max, 'time': 'first', 'index': lambda i: ','.join(i)})
# )
# other = copy.deepcopy(data.loc[data.operation != 'storage'])
# other = (
#     other.astype({'time': str})
#     .groupby(groupby_col, as_index=False)
#     # .agg({'Quantity': sum})
#     .agg({'Quantity': sum, 'time': lambda i: ','.join(sorted(set(i))), 'index': lambda i: ','.join(i)})
# )

# storage = (
#     (q.sort_values(by='Quantity', ascending=False))
#     .groupby(groupby_col, as_index=False)
#     .agg({'Quantity': max, 'time': 'first', 'index': lambda i: ','.join(i)})
# )

# data = pd.concat([storage, other]).to_dict(orient='records')
