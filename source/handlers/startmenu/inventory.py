import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import FSInputFile, InputMediaDocument

from filters.is_admin import UserIsAdmin
from filters.callbacks.startmenu import StartMenuActionCallbackData
from filters.callbacks.inventory import InventoryActionCallbackData
from utils.zapi.zapi import ZabbixAPI
from utils.cache import update_cache, load_from_cache
from keyboards.inventory.inventory import get_inventory_hostgroup_keyboard

inventory_router = Router()


@inventory_router.callback_query(
    UserIsAdmin(),
    InventoryActionCallbackData.filter(F.action == 'inventory_hostgroups' and F.type =='report')
    )
async def callback_inventory_hostgroup_report(callback: CallbackQuery, callback_data: CallbackData):
    message = await callback.message.edit_text("Загружаю отчёт... ⏳")
    zapi = ZabbixAPI()
    hostgroups_id = load_from_cache(callback.from_user.id, 'hostgroups')
    data = zapi.get_hosts_by_hostgroups_id(hostgroups_id)
    excel_fp = zapi.output.to_excel(data)
    await message.delete()
    await callback.message.answer_document(FSInputFile(excel_fp))
    
    if os.path.exists(excel_fp):
        os.remove(excel_fp)
    
    
@inventory_router.callback_query(
    UserIsAdmin(),
    InventoryActionCallbackData.filter(F.action =='inventory_hostgroups' and F.page_num and F.type != 'report')
    )
async def callback_inventory_hostgroup_page(callback: CallbackQuery, callback_data: CallbackData):
    cb_type = callback_data.type
    
    if cb_type.startswith('render'):
        msg = 'Меню ивентаризации'
        kb = get_inventory_hostgroup_keyboard(callback.from_user.id, callback_data.page_num)
        
        if kb:
            await callback.message.edit_text(msg, reply_markup=kb)
            
            if callback_data.page_num == 1:
                await callback.answer('Выберите группы и нажмите загрузить отчёт')
            return
    elif cb_type.startswith('groupid_'):
        chosen_group_id = callback_data.type.split('_')[-1]
        update_cache(callback.from_user.id, 'hostgroups', chosen_group_id)
        msg = 'Меню ивентаризации'
        kb = get_inventory_hostgroup_keyboard(callback.from_user.id, callback_data.page_num)
        
        if kb:
            try:
                await callback.message.edit_text(msg, reply_markup=kb)
                await callback.answer('Выберите группы и нажмите загрузить отчёт')
                return
            except TelegramBadRequest:
                await callback.answer('Ошибка обработки страницы')
                
    await callback.answer('Ошибка обработки страницы')

