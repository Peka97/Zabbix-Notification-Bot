#!/bin/bash

source /usr/lib/zabbix/alertscripts/Zabbix-Notification-Bot/.venv/bin/activate
python /usr/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/utils/alerting/send_to_bot.py "$@"