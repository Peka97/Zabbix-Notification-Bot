from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from filters.is_admin import UserIsAdmin
from keyboards.start import get_start_keyboard

start_router = Router()

@start_router.message(
    UserIsAdmin(),
    CommandStart(),
    )
async def cmd_start(message: Message):
    msg = 'Запуск сообщения по команде /start используя фильтр CommandStart()'
    kb = get_start_keyboard()
    await message.answer(msg, reply_markup=kb)