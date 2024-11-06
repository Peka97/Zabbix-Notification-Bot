import io
import json

from utils.logger import get_bot_logger

logger = get_bot_logger()

def update_cache(user_id: int, itemname, item) -> None:
    try:
        with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'r') as file:
            data = json.load(file)
    except json.decoder.JSONDecodeError:
        data = {}        
    
    try:
        if str(user_id) not in data.keys():
            data[str(user_id)] = []
            
        user_cache = data[str(user_id)]
        if user_cache and item in user_cache:
            user_cache.remove(item)
        elif user_cache:
            user_cache.append(item)
        else:
            data[str(user_id)] = [item, ]
                
    except Exception as err:
        logger.error(err, exc_info=True)

    else:
        with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'w') as file:
            json.dump(data, file, indent=4)

def load_from_cache(user_id: int, itemname) -> dict:
    try:
        with open(f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/misc/cache/users/{itemname}.json', 'r') as file:
            data = json.load(file)[str(user_id)]
        
    except (IndexError, json.decoder.JSONDecodeError):
        return []
    finally:
        return data

