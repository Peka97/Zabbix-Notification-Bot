from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CURRENT_CONFIG

def get_problem_keyboard(settings):
    url = f"https://{CURRENT_CONFIG.zabbix_api_external_ip}"
    item_id = settings["itemid"]
    event_id = settings["eventid"]
    trigger_id = settings["triggerid"]
    period = settings.get("graphperiod") # or CURRENT_CONFIG.period
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="График 📈",
            url=f"{url}/history.php?action=showgraph&itemids[]={item_id}&from=now-{period}",
        ),
        InlineKeyboardButton(
            text="Детали 📋",
            url=f"{url}/tr_events.php?triggerid={trigger_id}&eventid={event_id}",
        ),
    )
    
    keyboard.row(
        InlineKeyboardButton(
            text="Ticket 🗳",
            url=f"https://itsm/ticket-console-link",
        ),
        InlineKeyboardButton(
            text="Подтвердить 📌",
            callback_data="confirm_problem"
        )
    )
    return keyboard.as_markup()

def get_confirm_problem_keyboard():
    pass