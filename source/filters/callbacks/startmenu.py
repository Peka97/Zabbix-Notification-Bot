from aiogram.filters.callback_data import CallbackData


class StartMenuActionCallbackData(CallbackData, prefix='start'):
    action: str
    type: str


