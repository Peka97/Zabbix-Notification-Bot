import sys
sys.path.append(r'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source')
import asyncio

from utils.alerting.send_to_bot import send_message

script_path = __file__
send_to = 1387411715
subject = 'Problem: {EVENT.NAME}'
message = """<?xml version="1.0" encoding="UTF-8" ?>
    <root>
        <body>
            <messages>
    <![CDATA[
    - Критичность: High
- Хост: localhost \[`127.0.0.1`]
- Последнее значение: {ITEM.LASTVALUE1} ({TIME})
- Продолжительность: {EVENT.AGE}]]>
            </messages>
        </body>
        <settings>
            <severity>High</severity>
            <graphs>True</graphs>
            <graphperiod>43200</graphperiod>
            <keyboard>True</keyboard>
            <host>{HOST.HOST}</host>
            <itemid>47688</itemid>
            <triggerid>{TRIGGER.ID}</triggerid>
            <eventid>{EVENT.ID}</eventid>
            <actionid>{ACTION.ID}</actionid>
            <hostid>{HOST.ID}</hostid>
            <title><![CDATA[{HOST.HOST} - {EVENT.NAME}]]></title>
            <triggerurl><![CDATA[{TRIGGER.URL}]]></triggerurl>
            <eventtags><![CDATA[{EVENT.TAGS}]]></eventtags>
        </settings>
    </root>"""
    
params = [
    script_path,
    send_to,
    subject,
    message
]

if __name__ == '__main__':
    asyncio.run(send_message(params))
