from aiogram.filters.callback_data import CallbackData


class InventoryActionCallbackData(CallbackData, prefix='inventory'):
    action: str
    page_num: int
    type: str
