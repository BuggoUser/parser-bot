import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import parser_wb
import user_data

class AnswerPrice(StatesGroup):
    price = State()

bot = Bot(token='7858506497:AAH5h7Yg-Rp8ZSV-IWpwcfUsdrbXljt8Y-0')
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: Message):
    if message.chat.type == 'private':
        try:
            user_data.add_user(message.from_user.id)
            await message.answer(f'Добро пожаловать {message.from_user.first_name}! Я буду уведомлять вас о новых товарах FANBOX.'
            f'Используйте команду /send, чтобы получать рассылку.')
        except:
            await message.answer(
                f'Добро пожаловать {message.from_user.first_name}! Я буду уведомлять вас о новых товарах FANBOX.'
                f'Используйте команду /send, чтобы получать рассылку.')

@dp.message(Command('send'))
async def cmd_send(message: Message):
    if message.chat.type == 'private':
        if user_data.user_validate(message.from_user.id):
            await message.answer(f'Отлично! Я буду уведомлять вас о всех новинках! Чтобы отключить рассылку, используйте /stop')
        else:
            user_data.update_users(message.from_user.id, 1)
            await message.answer(f'Отлично! Я буду уведомлять вас о всех новинках! Чтобы отключить рассылку, используйте /stop')

async def send_data():
    data_for_send = parser_wb.insert_data_and_validate()
    users_for_send = user_data.get_all_users()
    count = 0

    if data_for_send:
        for user in users_for_send:
            for p in data_for_send:
                if user[1] == 1:
                    await bot.send_message(user[0], f'🔔 Новинка 🔔 \n \n'
                    f'*Товар:* {p[0]} \n'
                    f'*Цена:* {p[1]} *рублей* \n'
                    f'*Ссылка:* {p[3]} \n', parse_mode='Markdown')
                    count += 1
    else:
        print('Новинок нет!')

@dp.message(Command('stop'))
async def cmd_stop(message: Message):
    if message.chat.type == 'private':
        user_data.update_users(message.from_user.id, 0)
        await message.answer(f'Рассылка отключена! Если захотите вернуться, испольуйте /send')

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_data, 'cron', hour=20, minute=47)
    scheduler.start()
    try:
        parser_wb.start_db()
        user_data.start_db()
        await dp.start_polling(bot)
    except Exception as e:
        print(e)
    finally:
        parser_wb.close_db()
        user_data.close_db()
        print('Бд закрыта')

if __name__ == '__main__':
    asyncio.run(main())