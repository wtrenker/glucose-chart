'''
Copyright 2020 William Trenker

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http:www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
'''

import sqlite3
import pprint
import time
from datetime import datetime as dt
import datetime
import os
from General import decimalAverage, ymd, dateTimeStr
import System
# from Decimal import

# cutoffdate = dt(2019, 6, 30, 0, 0, 0)

dbMem = sqlite3.connect(':memory:')

# os.remove('/home/bill/dbs/meter.db')
dbMeter = sqlite3.connect('/home/bill/dbs/meter.db')
dbMeter.execute('delete from readings')
dbMeter.commit()

dbComments = sqlite3.connect("/home/bill/dbs/Comments.db")
# curMeter = dbMeter.cursor()

dbMem.execute('create table dates (date numeric)')
dbMem.execute('attach "/home/bill/dbstest/Bayer.db" as bayer')
dbMem.execute('insert into dates select distinct Test_Date from bayer.ResultData as rd order by rd.Test_Date')
dbGlucose = sqlite3.connect('/home/bill/dbs/glucose.db')
curDates = dbMem.execute('select * from dates')
for curDate in curDates.fetchall():
    curDate = curDate[0]
    minDate = dbMem.execute('select min(Test_Time), Measurement_Value from bayer.ResultData as brd where brd.Test_Date == ?', (curDate,))
    HMSmin, ReadingMin = minDate.fetchone()
    # print("curDate: ", curDate)
    maxDate = dbMem.execute('select max(Test_Time), Measurement_Value from bayer.ResultData as brd where brd.Test_Date == ?', (curDate,))
    HMSmax, ReadingMax = maxDate.fetchone()

    # HMSmin = dt.strptime(HMSmin, '%H:%M:%S')
    # HMSmax = dt.strptime(HMSmax, '%H:%M:%S')
    # delta = HMSmax - HMSmin
    # HMSavg = HMSmin + delta
    # HMSavg = HMSavg.strftime('%H:%M:%S')

    avgReading = decimalAverage(ReadingMin, ReadingMax)
    avgReading = float(avgReading)

    curDate = ymd(curDate)

    print(curDate, avgReading, type(curDate))
    # print(type(avgReading))
    try:
        dbMeter.execute('insert into readings (readingdate, avgreading) values (?, ?)', (curDate, avgReading))  #, (curDate, avgReading))
    except Exception as err:
        print('Error - insert into readings:', err)
    # print(ymd(curDate), HMSmin, HMSmax, HMSavg, ReadingMinat, ReadingMax, ReadingAvg)
    # pprint.pprint('-------------------------------------------')

dbMeter.commit()
dbMeter.close()

System.putLastReadingDateStr(dateTimeStr(datetime.now(), 'America/Vancouver', ampm=True, month=True, seconds=False))

# for Comment in dbComments.execute('select date, average, comment from comments'):
#     curDate, average, comment = Comment
#     print(curDate, type(curDate))
#     dbMeter.execute('insert into comments (date, reading, comment) values (?,?,?)', (curDate, average, comment))
# dbMeter.commit()
# dbGlucose.close()
