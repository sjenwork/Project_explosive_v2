import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, DECIMAL, Integer, NVARCHAR, BigInteger, BOOLEAN
from configparser import ConfigParser
from urllib.parse import quote
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


machineName = 'mssql_chemtest'
config = ConfigParser()
config.read('src/conf.ini')
server = config[machineName]['sql_server']
port = config[machineName]['sql_port']
table = config[machineName]['sql_table']
username = config[machineName]['sql_username']
password = quote(config[machineName]['sql_password'])
sqlalchemy_driver = config[machineName]['sql_sqlalchemy_driver']

conn = 'mssql+pymssql://username:password@server:port/table'

conn = (conn
        .replace('username', username)
        .replace('server', server)
        .replace('port', port)
        .replace('table', table)
        .replace('username', username)
        .replace('password', password)
        .replace('sqlalchemy_driver', sqlalchemy_driver)
        )
engine = create_engine(conn)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = session()


class explosive(Base):
    __tablename__ = 'ExplosiveMergeData'

    DeptID = Column(NVARCHAR(10), primary_key=True)
    DeclareTime = Column(NVARCHAR(20), primary_key=True)
    CASNo = Column(NVARCHAR(500), primary_key=True)
    ChemicalChnName = Column(NVARCHAR(500), primary_key=True)
    ChemicalEngName = Column(NVARCHAR(500), primary_key=True)
    SourceDept = Column(NVARCHAR(500), primary_key=True)
    ResponsibleName = Column(NVARCHAR(100), primary_key=True)
    ResponsibleTel = Column(NVARCHAR(50), primary_key=True)
    ResponsiblePhone = Column(NVARCHAR(50), primary_key=True)
    EmergencyName = Column(NVARCHAR(50), primary_key=True)
    EmergencyTel = Column(NVARCHAR(50), primary_key=True)
    EmergencyPhone = Column(NVARCHAR(50), primary_key=True)
    ComFacBizName = Column(NVARCHAR(100), primary_key=True)
    BusinessAdminNo = Column(NVARCHAR(100), primary_key=True)
    FactoryRegNo = Column(NVARCHAR(100), primary_key=True)
    ComFacBizAddress = Column(NVARCHAR(500), primary_key=True)
    PlaceType = Column(NVARCHAR(100), primary_key=True)
    RegionType = Column(NVARCHAR(100), primary_key=True)
    RegionName = Column(NVARCHAR(100), primary_key=True)
    ComFacBizTWD97X = Column(NVARCHAR(20), primary_key=True)
    ComFacBizTWD97Y = Column(NVARCHAR(20), primary_key=True)
    DeclareDate = Column(NVARCHAR(5), primary_key=True)
    ImportQuantity = Column(NVARCHAR(50), primary_key=True)
    ProductionQuantity = Column(NVARCHAR(50), primary_key=True)
    ProductionTWD97X = Column(NVARCHAR(20), primary_key=True)
    ProductionTWD97Y = Column(NVARCHAR(20), primary_key=True)
    UseageQuantity = Column(NVARCHAR(50), primary_key=True)
    UseageTWD97X = Column(NVARCHAR(20), primary_key=True)
    UseageTWD97Y = Column(NVARCHAR(20), primary_key=True)
    StorageQuantity = Column(NVARCHAR(50), primary_key=True)
    StorageTWD97X = Column(NVARCHAR(20), primary_key=True)
    StorageTWD97Y = Column(NVARCHAR(20), primary_key=True)
    ProductionZipCode = Column(NVARCHAR(5), primary_key=True)
    UseageZipCode = Column(NVARCHAR(5), primary_key=True)
    StorageZipCode = Column(NVARCHAR(5), primary_key=True)
    FCOUNTY = Column(NVARCHAR(255), primary_key=True)
    FTOWN = Column(NVARCHAR(255), primary_key=True)
    FCOUNTY_TOWN = Column(NVARCHAR(255), primary_key=True)
    CountyTownship = Column(NVARCHAR(255), primary_key=True)
    UpdateDate = Column(DateTime)
    IsMerge = Column(BOOLEAN)
    isProc = Column(BOOLEAN)


Base.metadata.create_all(engine)
# data = list(db.query(explosive).all())
filter = {'DeptID': ''}
filter = explosive.DeptID.op('regexp')(r'^MOST0001$')
data = db.query(explosive).filter(filter)
# pd.read_sql(data.statement, db.bind)
