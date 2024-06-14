import hashlib
from datetime import datetime
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from main import dp, bot
from data import texts
from keyboards import keyboards


async def authenticate_user(call: types.CallbackQuery) -> tuple:
    """
    Аутентификация пользователя и генерация ключа аутентификации.

    :tuple: Кортеж с хэшем ID пользователя и ключом аутентификации.
    """
    telegram_id_hash = hashlib.sha256((str(call.from_user.id) + config.TELEGRAM_SECRET_KEY).encode()).hexdigest()
    auth_key = hashlib.sha256((str(datetime.now().date()) + config.TELEGRAM_DATE_HASH_SECRET_KEY).encode()).hexdigest()
    return telegram_id_hash, auth_key


@dp.callback_query_handler(lambda call: call.data == 'get_all_offices')
async def get_all_offices(call: types.CallbackQuery):
    """
    Обработчик для команды получения информации обо всех офисах.
    """
    try:
        telegram_id_hash, auth_key = await authenticate_user(call)

        headers = {
            "X-AUTH-TYPE": "TELEGRAM-SECRET-KEY",
            "X-AUTH-KEY": auth_key
        }

        get_me_response = requests.get(f"{config.BASE_URL}/client/telegram/me/", params={"telegram_id_hash": telegram_id_hash}, headers=headers)
        if get_me_response.status_code != 200:
            await call.answer("Требуется привязка Telegram через веб-интерфейс.", show_alert=True)
            return

        get_me_data = get_me_response.json()

        get_offices_response = requests.get(f"{config.BASE_URL}/client/telegram/offices/", params={"telegram_id_hash": telegram_id_hash}, headers=headers)
        get_offices_data = get_offices_response.json()

        if get_offices_response.status_code == 200 and get_offices_data['result'] == 'success':
            first_name = get_me_data['data']['first_name']
            last_name = get_me_data['data']['last_name']
            offices = get_offices_data['data']

            office_count = len(offices)

            office_list = "\n".join([f"{office['display_name']} - {office['price']} рублей в месяц" for office in offices])

            message_text = texts.select_office_message.format(first_name, last_name, office_list)

            await bot.edit_message_text(
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                text=message_text,
                reply_markup=keyboards.office_selection(offices),
                parse_mode="html"
            )
        else:
            await call.answer("Произошла ошибка при получении данных об офисах.", show_alert=True)
    except Exception as e:
        print(e)
        await call.answer(f"Произошла ошибка", show_alert=True)


@dp.callback_query_handler(lambda call: 'open_office_' in call.data)
async def open_office(call: types.CallbackQuery):
    """
    Обработчик для команды получения подробностей об офисе.
    """
    try:
        telegram_id_hash, auth_key = await authenticate_user(call)
        office_id = call.data.replace('open_office_', '')

        headers = {
            "X-AUTH-TYPE": "TELEGRAM-SECRET-KEY",
            "X-AUTH-KEY": auth_key
        }

        get_office_response = requests.get(f"{config.BASE_URL}/client/telegram/offices/{office_id}/", params={"telegram_id_hash": telegram_id_hash}, headers=headers)
        
        if get_office_response.status_code != 200:
            await call.answer("У вас нет доступа к данному офису.", show_alert=True)
            return

        office_data = get_office_response.json()['data']
        
        await bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            text=texts.office_text.format(office_data['display_name'], office_data['floor'], office_data['area'], office_data['room_count']), 
            reply_markup=keyboards.lock_manager_keyboard(office_id),
            parse_mode="HTML"
        )

    except Exception as e:
        await call.answer(f"Произошла ошибка: {str(e)}", show_alert=True)
