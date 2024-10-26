import io
import json

def add_to_cache(user_id: int, itemname, item) -> None:
    try:
        with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'r') as file:
            data = json.load(file)
    except json.decoder.JSONDecodeError:
        data = {}
        data[str(user_id)] = [item, ]
        
    with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'w') as file:
        json.dump(data, file, indent=4)

def load_from_cache(user_id: int, itemname) -> dict:
    try:
        with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'r') as file:
            data = json.load(file)
        
    except (IndexError, json.decoder.JSONDecodeError):
        set_cache_template(user_id)
        
        with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'r') as file:
            data = json.load(file)
            
    finally:
        if data.get(str(user_id)):
            return data[str(user_id)]
        return []
            
        
def set_cache_template(user_id: int) -> None:
    itemnames = [
        'hostgroups'
    ]
    for itemname in itemnames:
        with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'w') as file:
            try:
                data = json.load(file)
            except io.UnsupportedOperation:
                data = {}
            data[str(user_id)] = []
            json.dump(data, file, indent=4)
