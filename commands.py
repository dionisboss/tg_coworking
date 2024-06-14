from aiogram import types
from main import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
import config
from data import texts
from keyboards import keyboards


async def mainMenu(message: types.Message, state: FSMContext):
    """
    Обработчик команды '/start'. Отправляет основное меню пользователю.

    :message: Сообщение, полученное от пользователя.
    """
    args = message.get_args()
    if not args:
        await bot.send_message(message.from_user.id, texts.mainMenuMessage, parse_mode="html", reply_markup=keyboards.mainMenuKeyboard)
    else:
        connect_telegram_response = requests.post(
            f"{config.BASE_URL}/client/auth/connect-telegram",
            params={"telegram_link_hash": args, "telegram_id": message.from_user.id}
        )
        if connect_telegram_response.status_code == 200:
            await message.answer("✅ Вы успешно привязали данный Telegram-профиль к аккаунту.")
            await bot.send_message(message.from_user.id, texts.mainMenuMessage, parse_mode="html", reply_markup=keyboards.mainMenuKeyboard)
        elif connect_telegram_response.status_code == 404:
            await message.answer("Операция невозможна. Пожалуйста, проверьте корректность ссылки.")
        else:
            await message.answer("Произошла ошибка при получении данных. Пожалуйста, попробуйте позже.")
