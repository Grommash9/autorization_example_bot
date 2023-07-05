import logging
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
from dataclasses import dataclass
from typing import Optional
API_TOKEN = '5821335363:AAF-ziCj8xMbc'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dataclass
class AuthorizationResp:
    message: str
    permission: bool
    url: Optional[str]


async def get_permission(user_id, permission_code):
    async with aiohttp.ClientSession() as session:
        query_params = f"?user_id={user_id}&permission_code={permission_code}"
        async with session.get(f'https://autorization-serivce-api.cakealliance.io/check_user/{query_params}') as resp:
            print(await resp.text())
            if resp.status != 200:
                # Тут можливо, що айпі немає в списку білого листа, переконатися самому вже або коду нема в базі
                raise ConnectionError("Немає з'єднання із сервісом авторизації!")
            resp_payload = await resp.json()

            return AuthorizationResp(resp_payload.get('message'), resp_payload.get('permission', False), resp_payload.get('url'))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привіт я бот для перевірки роботи системи доступу! У мене є лише одна команда /pay")


@dp.message_handler(commands=['pay'])
async def send_welcome(message: types.Message):
    try:
        permission_info = await get_permission(message.from_user.id, 'test_bot_pay_func')
    except Exception as e:
        await bot.send_message(message.from_user.id, f'Помилка: {e}')
        return
    if permission_info.permission:
        await message.reply('Доступ є')
        return

    await message.reply('Доступ нема\n' f'{permission_info.url}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)