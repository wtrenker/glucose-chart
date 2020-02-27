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

from bottle import route, default_app, HTTPResponse, run, jinja2_view, url, get, post, request, html_escape,\
    response, redirect, debug, jinja2_template, MultiDict, post
from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mpd
import numpy as np
from datetime import datetime
from General import verify_password, decimalAverage, dateTimeStr, dbFileName
import pytz
from io import BytesIO
from pathlib import Path
# import Sessions, HTTPCookie, System
import System
import sys
import time

dbPath = Path(f'./db/meter.db')
# dbPath = Path(dbFile)
db = Database()

class Readings(db.Entity):
    readingdate = PrimaryKey(str)
    avgreading = Optional(float)
DATE = 0
AVERAGE = 1

class Comments(db.Entity):
    date = PrimaryKey(str)
    reading = Optional(float)
    comment = Optional(str)


db.bind(provider='sqlite', filename=str(dbPath), create_db=False)
# db.bind(provider='sqlite', filename="db/meter.db", create_db=False)
db.generate_mapping(create_tables=False)

# zulu = pytz.timezone('UTC')
pst = pytz.timezone("America/Vancouver")

def renderChart(request):

    DateCombined = []
    CommentDateCombined = []
    DailyAverageCombined = []
    CommentCombined = []
    CommentReadingCombined = []

    dATE = 0
    aVERAGE = 1

    with db_session:
        qry = select((r.readingdate, r.avgreading) for r in Readings).order_by(1)
        try:
            recs = qry.fetch()
        except Exception as e:
            print(e)
        for rec in recs:
            dtdate, avg = rec
            dtdate = datetime.strptime(dtdate, "%Y-%m-%d")
            DateCombined.append(dtdate)
            DailyAverageCombined.append(avg)

        qry = select((c.date, c.reading, c.comment) for c in Comments).order_by(1)
        try:
            recs = qry.fetch()
        except Exception as e:
            print(e)
        for rec in recs:
            dtdate, reading, comment = rec
            dtdate = datetime.strptime(dtdate, "%Y-%m-%d")
            CommentDateCombined.append(dtdate)
            CommentReadingCombined.append(reading)
            CommentCombined.append(comment)

    DateCombined = mpd.date2num(DateCombined)
    CommentDateCombined = mpd.date2num(CommentDateCombined)

    fig, ax1 = plt.subplots()

    lineTarg = ax1.axhline(y=6, linewidth=4, color='k', label='Glucose Target Range')
    ax1.axhline(y=9, linewidth=4, color='k')

    background = 0.30

    lineCombined, = ax1.plot_date(DateCombined, DailyAverageCombined, label='Daily Blood Glucose', linestyle='-',
                                  linewidth=1, color='r', marker=None, tz=pst)  #

    ax1.yaxis.grid(True, linewidth=1)

    for i in range(len(CommentDateCombined)):
        # text = f'<---{(CommentCombined[i], CommentDateCombined[i])}'
        text = f'<---{CommentCombined[i]}'
        # return pprint.pformat((text, CommentDateCombined[i], CommentAverageCombined[i]))
        ax1.annotate(text, (CommentDateCombined[i], CommentReadingCombined[i]), fontsize=14,
                     color='b', weight='bold')  # , rotation=0,
#-------------------------
    DateRange = np.concatenate((DateCombined,))
    minDate = min(DateRange)
    maxDate = max(DateRange)
    ax1.set_xlim(minDate, maxDate)

    df = mpl.dates.DateFormatter('%b-%d', tz=pst)
    ax1.xaxis.set_major_formatter(df)
    ax1.tick_params(which='major', width=2.0, length=4.0)  # , labelsize=10)
    xlocator = mpl.dates.DayLocator(tz=pst)
    ax1.xaxis.set_minor_locator(xlocator)

    plt.gcf().autofmt_xdate()

    z = np.polyfit(DateCombined, DailyAverageCombined, 2)
    # z = np.polynomial.chebyshev.chebfit(DateCombined, DailyAverageCombined, 2)
    p = np.poly1d(z)
    trendLine, = ax1.plot_date(DateCombined, p(DateCombined), 'k--', label='Trend Line')

    # ax1.legend(handles=[lineCombined, trendLine, lineTarg], loc='upper left') # , loc='lower right' 'best'
    ax1.legend(handles=[lineCombined, lineTarg, trendLine], loc='upper right')  #  , loc='lower right' 'best'

    plt.title('Average Daily Blood Glucose (Jardiance Trial)', loc='left')
    plt.title('William Trenker')
    #
    # sessionID = HTTPCookie.getSessionCookie(request)
    nowstr = System.getLastReadingDateStr()
    # nowstr = dateTimeStr(datetime.now(), "America/Vancouver")
    dbNow = f'({dbFileName}) last updated: {nowstr}'
    plt.title(dbNow, fontsize=10, loc='right')
    #
    ax1.set_xlabel('Date (2019 - 2020)')  # Note that this won't work on plt or ax2
    ax1.set_ylabel('Blood Glucose (mmol/L)')

    fig.set_size_inches(16, 8.5)
    # fig.tight_layout()

    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img
    # return send_file(img, mimetype='image/png')

@get('/', name='home')
@get('/home', name="homepage")
def home():
    respData = MultiDict(url=url, title='Blood Glucose')
    return jinja2_template('Home.jinja2', respData, template_lookup=['templates'])

@get('/averages', name="averages")
def averages():
    # sessionID = HTTPCookie.getSessionCookie(request)
    respData = dict(url=url, title='Blood Glucose', timestamp=time.time())  #, sessionID=sessionID)
    return jinja2_template('Averages.jinja2', respData, template_lookup=['templates'])

@get('/chart', name='chart')
def chart():
    # log('chart', 'HTTPResponse')
    img = renderChart(request)
    resp = HTTPResponse(body=img, status=200)
    resp.set_header('content_type', 'image/png')
    return resp

app = default_app()

@app.error(404)
def error404handler(error):
    f = request.fullpath
    respData = MultiDict(dict(f=f))
    return jinja2_template('405.jinja2', respData, template_lookup=['templates'])

@app.error(405)
def error405handler(error):
    f = request.fullpath
    respData = MultiDict(dict(f=f))
    return jinja2_template('405.jinja2', respData, template_lookup=['templates'])

@app.error(500)
def error500handler(error):
    f = request.fullpath
    respData = MultiDict(dict(f=f))
    return jinja2_template('500.jinja2', template_lookup=['templates'])



if __name__ == '__main__':
    run(host='localhost', port=8081, debug=True)
# renderChart(request)
