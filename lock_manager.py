from aiogram import types
from main import dp, bot
import requests
import config
from data import texts
import hashlib
from datetime import datetime


async def toggle_lock(call: types.CallbackQuery, action: str):
    """
    Функция для открытия или закрытия офиса.

    :action: Действие, которое нужно выполнить ('lock' для закрытия, 'unlock' для открытия).
    """
    try:
        telegram_id_hash = hashlib.sha256((str(call.from_user.id) + config.TELEGRAM_SECRET_KEY).encode()).hexdigest()
        auth_key = hashlib.sha256((str(datetime.now().date()) + config.TELEGRAM_DATE_HASH_SECRET_KEY).encode()).hexdigest()
        office_id = call.data.split('_')[-1]

        headers = {
            "X-AUTH-TYPE": "TELEGRAM-SECRET-KEY",
            "X-AUTH-KEY": auth_key
        }

        toggle_lock_response = requests.post(f"{config.BASE_URL}/client/telegram/offices/{office_id}/{action}/", params={"telegram_id_hash": telegram_id_hash}, headers=headers)
        
        if toggle_lock_response.status_code != 200:
            await call.answer(f"Не удалось {action} замок.", show_alert=True)
            return
        
        await call.answer(f"Замок успешно {('открыт' if action == 'unlock' else 'закрыт')}.", show_alert=True)

    except Exception as e:
        await call.answer(f"Произошла ошибка: {str(e)}", show_alert=True)


@dp.callback_query_handler(lambda call: 'unlock_office_' in call.data)
async def unlock_office(call: types.CallbackQuery):
    """
    Обработчик для команды открытия офиса.
    """
    await toggle_lock(call, action="unlock")


@dp.callback_query_handler(lambda call: 'lock_office_' in call.data)
async def lock_office(call: types.CallbackQuery):
    """
    Обработчик для команды закрытия офиса.
    """
    await toggle_lock(call, action="lock")