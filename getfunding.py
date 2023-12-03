import os
import sys
import asyncio
import time
import requests
import csv
from apikey import API_KEY
sys.path.append('../../../')

from datetime import datetime



from bfxapi import Client

API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")

bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

dt = datetime(2022, 1, 1)
starttime = int(round(dt.timestamp() * 1000))

dt = datetime(2022, 12, 31)
endtime = int(round(dt.timestamp() * 1000))



def ms2datestr(ms):
    d = datetime.fromtimestamp(ms/1000)
    return d.strftime("%Y-%m-%d")
#    return d.ctime()


BASE_URL = 'https://www.alphavantage.co/query'

def createURL(base, **kwargs):
    argStr = '&'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
    urlStr = base + '?' + argStr
    return urlStr

def qryDaSngl(symbol='IBM', function='TIME_SERIES_DAILY', outputsize='compact'):
    with requests.Session() as s:
        download = s.get(createURL(BASE_URL, function=function,
            symbol=symbol, market='EUR',
                         datatype='csv', outputsize=outputsize, apikey=API_KEY))
    contentStr = download.content.decode('utf-8')
    cr = csv.reader(contentStr.splitlines(), delimiter=',')
    tsList = list(cr)
    return (tsList[0], tsList[1:])

def ts2dict(ts):
    return ({ts[0][0]: ts[0][1:]}, {e[0]: e[1:] for e in ts[1]})

async def qryData(symbols, function='TIME_SERIES_DAILY', outputsize='compact'):
    dvs = {}
    for symbol in symbols:
        dk, dv = ts2dict(qryDaSngl(symbol, function, outputsize))
        for k, v in dv.items():
            if k not in dvs:
                dvs[k] = {}
            dvs[k][symbol] = v
    return dvs

async def log_funding_credits_history(cur='FIL'):
  exch = await qryData([cur], 'DIGITAL_CURRENCY_WEEKLY', 'full')
  #print(exch)
  excht = {datetime.fromisoformat(k).timestamp(): v for k, v in exch.items()}
  #print(excht)
  exch = {datetime.fromtimestamp(k+i*24*60*60).isoformat()[:10]: v for k, v in excht.items() for i in range(7)}
  #print(exch)
  credit = []
  interv = 2678400000
  t = starttime
  while(t+interv < endtime):
    credit += await bfx.rest.get_funding_credit_history('f{}'.format(cur),
          t, t+interv, 500)
    t += interv
  credit += await bfx.rest.get_funding_credit_history('f{}'.format(cur),
          t, endtime, 500)
  total = 0
  print ("Funding credit history:")
  print(" SYM     BEGIN       END        DAYS \
          AMOUNT       RATE       EARNINGS (cur)   PRICE (EUR)  EARNINGS (EUR)")
  for c in credit:
      days = (c.mts_update-c.mts_create)/1000/60/60/24
      date = ms2datestr(c.mts_create)
      try:
        xch = float(exch[date][cur][0])
      except Exception as e:
        xch = 0
        print(e)
      earn = c.amount * c.rate * days
      total += xch*earn
      print("{}  {}  {}  {:10.5f}  {:16.11f}  {:14.11f}  {:18.15f}  {:12.5f}  {:18.15f}".format(c.symbol, date,
        ms2datestr(c.mts_update), days, c.amount, c.rate, earn, xch, xch*earn))

  print("                                       \
                                                                      --------------")
  print("                                       \
                                                                       {:18.15f}".format(total))

async def run():
  await log_funding_credits_history('FIL')
  #await log_funding_credits_history('LUNA')
  await log_funding_credits_history('TRX')
  await log_funding_credits_history('MKR')
  #await log_funding_credits_history('AXS')
  await log_funding_credits_history('NEO')



t = asyncio.ensure_future(run())
asyncio.get_event_loop().run_until_complete(t)
