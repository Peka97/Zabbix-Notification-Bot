import json
from pprint import pprint
import asyncio


# from utils.cache import load_from_cache, add_to_cache
from utils.zapi.zapi import ZabbixAPI
from utils.alerting.send_to_bot import send_message

# add_to_cache('123123123123', 'hostgroups', '12321')
# print(load_from_cache('1387411715', 'hostgroups'))

if __name__ == '__main__':
    # zapi = ZabbixAPI()
    # pprint(zapi.get_availability_report())
    send_to = '1387411715'
    subject = "🧨 *Problem: High memory utilization (>1% for 5m)*"
    text = """\r
    \r- Критичность: 🟡Average
    \r- Хост: verbalvoyager \[`158.160.153.184`]
    \r- Последнее значение: 23.82 % (14:09:09)
    \r- Продолжительность: 2s"""
    settings = "{\"severity\": \"🟡Average\", \"graphs\": \"True\", \"graphperiod\": \"43200\", \"keyboard\": \"True\", \"host\": \"verbalvoyager\", \"itemid\": \"47736\", \"triggerid\": \"23841\", \"eventid\": \"1732036\", \"actionid\": \"11\", \"hostid\": \"10638\", \"title\": \"verbalvoyager - High memory utilization (>1% for 5m)\"}"
    if isinstance(settings, str):
        settings = json.loads(settings)
    asyncio.run(send_message(send_to, subject, text, settings))
