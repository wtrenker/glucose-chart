import sqlite3
import pprint
import time
from datetime import datetime as dt
# import datetime
import os

cutoffdate = dt(2019, 6, 30, 0, 0, 0)

def ymd(msdate):
    datetime = dt.fromtimestamp(msdate // 1000)
    dated = datetime.strftime("%Y-%m-%d")
    return dated

dbMem = sqlite3.connect(':memory:')
dbMem.execute('create table dates (date numeric)')
dbMem.execute('attach "/home/bill/dbstest/Bayer.db" as bayer')
dbMem.execute('insert into dates select distinct Test_Date from bayer.ResultData as rd order by rd.Test_Date')
curDates = dbMem.execute('select * from dates')
for curDate in curDates.fetchall():
    minDate = dbMem.execute('select Test_Date, min(Test_Time), Measurement_Value from bayer.ResultData as brd where brd.Test_Date == ?', curDate)
    YMD, HMS, Reading = minDate.fetchone()
    print(ymd(YMD), HMS, Reading)

    maxDate = dbMem.execute('select Test_Date, max(Test_Time), Measurement_Value from bayer.ResultData as brd where brd.Test_Date == ?', curDate)
    YMD, HMS, Reading = maxDate.fetchone()
    print(ymd(YMD), HMS, Reading)

    pprint.pprint('-------------------------------------------')

exit()


    ymdMeter = ymd(result[0])
    resultdate = dt.strptime(ymdMeter, '%Y-%m-%d')
    if resultdate > cutoffdate:
        continue
    hmsMeter = result[1]
    dbMem.execute('insert into meterdates values (?, ?)', (ymdMeter, hmsMeter))
pprint.pprint(dbMem.execute('select * from meterdates').fetchall())

# dbGlucose = sqlite3.connect('/home/bill/dbs/glucose.db')
# cursorGlucose = dbGlucose.execute('select distinct date, am, pm from Readings order by (1)')
# for reading in cursorGlucose.fetchall():
#     print(reading)



# pprint.pprint(cursorMeter.fetchall())
# d = dbMem.execute('select * from meterdates').fetchall()
# print(d)

