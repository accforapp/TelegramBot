import requests
import json
import datetime
import time

start_time = time.time()


def load():
    result = {}
    ls = []
    n_days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
              7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    day = datetime.date.today().day
    month = datetime.date.today().month
    l_range = 0
    with open('rate_archive.json', 'r') as read_file:
        data = json.load(read_file)

    if int(data[0]['date'][:2]) != datetime.date.today().day:
        l_range = datetime.date.today().day - int(data[0]['date'][:2])
    if l_range > 7:
        l_range = 7

    if l_range != 0:
        for i in range(l_range):

            URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date=' \
                  + datetime.date(datetime.date.today().year, month, day).strftime('%d.%m.%Y')
            archResp = json.loads(requests.get(URL).text)

            day -= 1
            if day < 1:
                month -= 1
                day = n_days[month]
            k = i + 3
            for j in range(len(data) - 1, k - 1, -1):
                buf = data[j - k]
                data[j] = buf

            for r in archResp['exchangeRate'][1:]:
                if r['currency'] == 'USD' or r['currency'] == 'EUR' or r['currency'] == 'RUB':
                    result = dict(date=str(archResp['date']), ccy=r['currency'], sale=str(r['saleRate']),
                                  buy=str(r['purchaseRate']))

                    data[k - 1] = result
                    k -= 1

        with open('rate_archive.json', 'w') as write_file:
            json.dump(data, write_file)


print(time.time() - start_time)
